# -*- coding: utf-8 -*-
import datetime
from os import path

import lxml
import pytz

import import_jobs
from seo.tests.factories import BusinessUnitFactory
from seo.tests.setup import DirectSEOBase
import transform


utc = pytz.UTC


class JobsFStoJsonTest(DirectSEOBase):
    fixtures = ['import_jobs_testdata.json', 'countries.json']

    def setUp(self):
        super(JobsFStoJsonTest, self).setUp()
        self.document = path.join(path.dirname(__file__), 'data/789274C9-D0AA-49D6-8257-A8E977576183.xml')
        self.bu = BusinessUnitFactory()
        import_jobs.add_company(self.bu)

    def test_dates_have_timezones(self):
        """Assert that dates on imports can be resolved to specifc utc times"""

        with open(self.document) as f:
            etree = lxml.etree.fromstring(f.read())

        result = transform.hr_xml_to_json(etree, self.bu)

        # Check date_updated
        date_updated = result['date_updated']

        # Assert it has a timezone
        self.assertIsNotNone(date_updated.tzinfo,
                             msg="The date_updated should have a "\
                                 "timezone associated with it.")

        # Assert the datetime is correct when converted to UTC.
        actual_utc = date_updated.astimezone(pytz.UTC)
        expected = datetime.datetime(2016, 01, 27, 20, 57, 03, 997000, pytz.UTC)
        self.assertEqual(actual_utc, expected,
            msg="date_updated is '%s', it should equal '%s'" % (
                date_updated.astimezone(pytz.UTC),
                expected.isoformat()))

        # Check date_created
        date_new = result['date_new']

        # Assert it has a timezone
        self.assertIsNotNone(date_new.tzinfo,
                             msg="The date_new should have a "\
                                 "timezone associated with it.")

        # Assert the datetime is correct when converted to UTC.
        actual_utc = date_new.astimezone(pytz.UTC)
        expected = datetime.datetime(2016, 01, 27, 20, 57, 03, 997000, pytz.UTC)
        self.assertEqual(actual_utc, expected,
            msg="date_new is '%s', it should equal '%s'" % (
                date_new.astimezone(pytz.UTC),
                expected.isoformat()))
