#!/usr/bin/env python2
from datetime import datetime
import json
import os
import sys

from dateutil import parser
import boto
from pymongoenv import connect_db

sys.path.insert(0, '/home/web/MyJobs/MyJobs-urls')

from secrets import AWS_ACCESS_KEY_ID, AWS_SECRET_KEY


def get_log_lines(file_name):
    """
    Returns the text contained within the file pointed to by "file_name". Text
    is unquoted and split into lines.
    """
    boto_connection = boto.connect_s3(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_KEY)
    log_bucket = boto_connection.get_bucket('my-jobs-logs', validate=False)
    log = log_bucket.get_key(file_name)
    contents = log.get_contents_as_string().decode('string_escape')
    return contents.splitlines()


def to_mongo(file_name):
    """
    Inserts the constituent lines of the file pointed to by "file_name" into
    a Mongo database.
    """
    analytics = connect_db().db

    base_name = os.path.basename(file_name)

    # If you're comparing this with store.py from MyJobs-Analytics, you'll
    # notice that we're using file_name here instead of base_name. Analytics
    # log files are stored on the analytics servers themselves, while redirect
    # stores its logs in s3. This is one way to differentiate the two.
    count = analytics.files.find_one({"file": file_name}) or 0
    if count:
        # This file was already processed.
        # TODO: Add ability to upsert based on this?
        return

    lines = get_log_lines(file_name)

    # All redirect logs are named using the same format, which differs from
    # analytics logs - "ex%y%m%d%H%M%S.log"; strip "ex" and the extension to
    # get our timestamp.
    timestamp = os.path.splitext(base_name)[0][2:]
    file_created = datetime.strptime(timestamp, "%y%m%d%H%M%S")

    file_id = analytics.files.insert_one({
        "file": file_name, "line_count": len(lines),
        "file_created": file_created}).inserted_id

    json_lines = []
    # Denotes if the file was inserted successfully in its entirety. Toggled if
    # we can't parse a line as JSON.
    success = True
    for line in lines:
        # Try to parse each line as JSON. There may or may not be invalid data
        # in the file; Don't crash and burn if so.
        try:
            json_line = json.loads(line)
        except ValueError:
            success = False
        else:
            # '"-"' is valid JSON but insert_many requires a list of
            # dictionaries. If "json_line" is a string, it's not a
            # document we wish to keep.
            if not isinstance(json_line, basestring):
                for key, value in json_line.items():
                    if key in ['to', 'sv', 'nv', 'fv'] and value:
                        # parser.parse('') results in today's date; we probably
                        # don't want that. Ensure the parameter has a value.
                        try:
                            json_line[key] = parser.parse(value)
                        except (ValueError, TypeError):
                            pass
                    elif isinstance(value, basestring) and value.isdigit():
                        json_line[key] = int(value)
                        if key == 'time':
                            json_line[key] = datetime.fromtimestamp(
                                json_line[key])
                json_line['file_id'] = file_id
                json_lines.append(json_line)

    if json_lines:
        # It's possible the file is blank or we failed parsing all lines.
        # TODO: Auditing procedure that compares "line_count" from the "files"
        #     collection with the number of items related to that file in the
        #     "analytics" collection.
        analytics.analytics.insert_many(json_lines)
    analytics.files.update({'_id': file_id},
                                  {'$set': {'success': success}})


if __name__ == '__main__':
    # Do some magic.
    if len(sys.argv) >= 2:
        [to_mongo(file_) for file_ in sys.argv[1:]]
