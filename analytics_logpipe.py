#!/usr/bin/env python2
import sys
import json
import boto3
import time
from botocore.exceptions import ClientError

import secrets


def process_lines(kinesis, lines):
    """Read log lines and send them to AWS Kinesis.
    Runs string unescaping and parses line to get an ip for the partition key.

    Also converts some string values to ints.
    """
    for line in lines:
        # Strip of the string escaping.
        data = line.decode('string_escape')

        # Parse the json or give up.
        parsed = None
        try:
            parsed = json.loads(data)
        except ValueError:
            continue

        # Give up if we are looking at something wierd. i.e. "-"
        if not isinstance(parsed, dict):
            continue

        partition_key = parsed.get('ip')

        # Convert some strings to ints, etc.
        massaged = massage_log_line(parsed)

        data = json.dumps(massaged)

        needs_resend = u'ProvisionedThroughputExceededException'
        for attempts in xrange(1, 8):
            try:
                result = kinesis.put_record(
                    StreamName=secrets.LOG_TO_STREAM,
                    Data=data,
                    PartitionKey=partition_key)
                error_code = result.get('ErrorCode')
                if error_code is None:
                    break
                elif error_code == needs_resend:
                    print >>sys.stderr, "Attempt: %d" % attempts, repr(result)
                    time.sleep(2 ** attempts)
                    continue
                else:
                    print >>sys.stderr, repr(result)
            except ClientError as e:
                print >>sys.stderr, e.message


def massage_log_line(json_line):
    """Convert some values from strings to more meaningful types."""
    result = dict(json_line)
    for key, value in json_line.items():
        if isinstance(value, basestring) and value.isdigit():
            int_val = int(value)
            if isinstance(int_val, long):
                # We have an undefined number of fields that can
                # potentially contain guids. It is possible for
                # a guid to be comprised entirely of digits. Don't
                # insert a guid as a number - Mongo can only take
                # 8-byte ints.
                continue

            result[key] = int_val
    return result


if __name__ == '__main__':
    kinesis = boto3.client(
        'kinesis',
        region_name=secrets.AWS_DEFAULT_REGION,
        aws_access_key_id=secrets.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=secrets.AWS_SECRET_KEY)

    process_lines(kinesis, sys.stdin)
