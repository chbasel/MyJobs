import json

from pymongoenv import connect_db
from dateutil import parser as dateparser

from myjobs.tests.setup import MyJobsBase
import myreports.models as myreports_models

from django.core.urlresolvers import reverse

from analytics.api import (get_available_analytics, get_report_info,
                           dynamic_chart)


class TestApi(MyJobsBase):
    collection_names = ['job_views']

    def setUp(self):
        super(TestApi, self).setUp()
        self.maxDiff = 10000
        self.role.add_activity("view analytics")
        self.rit_analytics = myreports_models.ReportingType.objects.create(
            reporting_type="web-analytics",
            description="Web Analytics",
            is_active=True)

        self.rt_job_titles = myreports_models.ReportType.objects.create(
            report_type="job-titles",
            description="Job Titles",
            is_active=True)
        self.rt_job_found_on = myreports_models.ReportType.objects.create(
            report_type="job-found-on",
            description="Site Found On",
            is_active=True)
        self.rt_job_locations = myreports_models.ReportType.objects.create(
            report_type="job-locations",
            description="Job Locations",
            is_active=True)

        myreports_models.ReportingTypeReportTypes.objects.create(
            reporting_type=self.rit_analytics,
            report_type=self.rt_job_titles,
            is_active=True)
        myreports_models.ReportingTypeReportTypes.objects.create(
            reporting_type=self.rit_analytics,
            report_type=self.rt_job_found_on,
            is_active=True)
        myreports_models.ReportingTypeReportTypes.objects.create(
            reporting_type=self.rit_analytics,
            report_type=self.rt_job_locations,
            is_active=True)

        unagg = myreports_models.DataType.objects.create(
                data_type="Unaggregated")

        self.config_job_titles = myreports_models.Configuration.objects.create(
            name="Job Titles",
            is_active=True)
        self.config_found_on = myreports_models.Configuration.objects.create(
            name="Found On",
            is_active=True)
        self.config_job_locations = (
            myreports_models.Configuration.objects.create(
                name="Job Locations",
                is_active=True))

        self.rtdt_job_titles = (
            myreports_models.ReportTypeDataTypes.objects.create(
                report_type=self.rt_job_titles,
                data_type=unagg,
                is_active=True,
                configuration=self.config_job_titles))
        self.rtdt_job_found_on = (
            myreports_models.ReportTypeDataTypes.objects.create(
                report_type=self.rt_job_found_on,
                data_type=unagg,
                is_active=True,
                configuration=self.config_found_on))
        self.rtdt_job_locations = (
            myreports_models.ReportTypeDataTypes.objects.create(
                report_type=self.rt_job_locations,
                data_type=unagg,
                is_active=True,
                configuration=self.config_job_locations))

        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_job_titles,
            order=1,
            column_name="title",
            filter_interface_type='string',
            filter_interface_display='Job Title',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_job_titles,
            order=2,
            column_name="job_guid",
            filter_interface_type='string',
            filter_interface_display='Job Id',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_job_titles,
            order=3,
            column_name="country",
            filter_interface_type='map:world',
            filter_interface_display='Country',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_job_titles,
            order=4,
            column_name="state",
            filter_interface_type='map:nation',
            filter_interface_display='State',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_job_titles,
            order=5,
            column_name="city",
            filter_interface_type='map:state',
            filter_interface_display='City',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_job_titles,
            order=6,
            column_name="found_on",
            filter_interface_type='string',
            filter_interface_display='Found on',
            multi_value_expansion=0,
            is_active=True)

        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_found_on,
            order=1,
            column_name="found_on",
            filter_interface_type='string',
            filter_interface_display='Found On',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_found_on,
            order=2,
            column_name="title",
            filter_interface_type='string',
            filter_interface_display='Job Title',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_found_on,
            order=3,
            column_name="job_guid",
            filter_interface_type='string',
            filter_interface_display='Job Id',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_found_on,
            order=4,
            column_name="country",
            filter_interface_type='map:world',
            filter_interface_display='Country',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_found_on,
            order=4,
            column_name="state",
            filter_interface_type='map:nation',
            filter_interface_display='State',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_found_on,
            order=6,
            column_name="city",
            filter_interface_type='map:state',
            filter_interface_display='City',
            multi_value_expansion=0,
            is_active=True)

        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_job_locations,
            order=1,
            column_name="country",
            filter_interface_type='map:world',
            filter_interface_display='Country',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_job_locations,
            order=2,
            column_name="state",
            filter_interface_type='map:nation',
            filter_interface_display='State',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_job_locations,
            order=3,
            column_name="city",
            filter_interface_type='map:state',
            filter_interface_display='City',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_job_locations,
            order=4,
            column_name="found_on",
            filter_interface_type='string',
            filter_interface_display='Found On',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_job_locations,
            order=5,
            column_name="title",
            filter_interface_type='string',
            filter_interface_display='Job Title',
            multi_value_expansion=0,
            is_active=True)
        myreports_models.ConfigurationColumn.objects.create(
            configuration=self.config_job_locations,
            order=6,
            column_name="job_guid",
            filter_interface_type='string',
            filter_interface_display='Job Id',
            multi_value_expansion=0,
            is_active=True)

    def populate_mongo_data(self):
        job_views = connect_db().db.job_views
        mongo_data = [
            {
                "time_first_viewed": dateparser.parse("10/17/2012 01:00:00"),
                "country": "GER",
                "state": "Gutentag",
                "city": "Braunshweiger",
                "found_on": "www.google.de",
                "view_count": 3,
             },
            {
                "time_first_viewed": dateparser.parse("10/18/2012 01:00:00"),
                "country": "GER",
                "state": "Gutentag",
                "city": "Braunshweiger",
                "found_on": "www.google.de",
                "view_count": 3,
             },
            {
                "time_first_viewed": dateparser.parse("10/18/2012 01:00:00"),
                "country": "USA",
                "state": "IN",
                "city": "Peru",
                "found_on": "www.google.com",
                "view_count": 2,
             },
            {
                "time_first_viewed": dateparser.parse("10/18/2012 01:00:00"),
                "country": "USA",
                "state": "IN",
                "city": "Indianapolis",
                "found_on": "www.google.com",
                "view_count": 7,
             },
            {
                "time_first_viewed": dateparser.parse("10/18/2012 01:00:00"),
                "country": "USA",
                "state": "MI",
                "city": "Muskegon",
                "found_on": "www.google.com",
                "view_count": 1,
             },
            ]
        job_views.insert_many(mongo_data)

    def test_available(self):
        response = self.client.get(reverse(get_available_analytics))
        result = json.loads(response.content)
        expected = {
            'reports': [
                {
                    'value': 'job-locations',
                    'display': 'Job Locations',
                },
                {
                    'value': 'job-titles',
                    'display': 'Job Titles',
                },
                {
                    'value': 'job-found-on',
                    'display': 'Site Found On',
                },
            ],
        }
        self.assertEqual(expected, result)

    def test_report_info(self):
        response = self.client.get(
            reverse(get_report_info),
            {'analytics_report_id': 'job-locations'})
        result = json.loads(response.content)
        expected = {
            'dimensions': [
                {
                    'value': 'country',
                    'display': 'Country',
                    'interface_type': 'map:world',
                },
                {
                    'value': 'state',
                    'display': 'State',
                    'interface_type': 'map:nation',
                },
                {
                    'value': 'city',
                    'display': 'City',
                    'interface_type': 'map:state',
                },
                {
                    'value': 'found_on',
                    'display': 'Found On',
                    'interface_type': 'string',
                },
                {
                    'value': 'title',
                    'display': 'Job Title',
                    'interface_type': 'string',
                },
                {
                    'value': 'job_guid',
                    'display': 'Job Id',
                    'interface_type': 'string',
                },
            ]
        }
        self.assertEqual(expected, result)

    def test_report_info_no_id(self):
        response = self.client.get(reverse(get_report_info))
        self.assertEqual(400, response.status_code)
        result = json.loads(response.content)
        fields = [i['field'] for i in result]
        self.assertIn('analytics_report_id', fields)

    def test_report_info_bad_id(self):
        response = self.client.get(
            reverse(get_report_info),
            {'analytics_report_id': 'zzzzz'})
        self.assertEqual(400, response.status_code)
        result = json.loads(response.content)
        fields = [i['field'] for i in result]
        self.assertIn('analytics_report_id', fields)

    def test_valid_dynamic_charts_request(self):
        expected_rows = [{u"country": u"USA", u"job_views": 10},
                         {u"country": u"GER", u"job_views": 3}]
        self.populate_mongo_data()
        request_data = {"date_start": "10/18/2012 00:00:00",
                        "date_end": "10/19/2012 00:00:00",
                        "active_filters": [],
                        "report": "job-locations"}
        response = self.client.post(reverse(dynamic_chart),
                                    {"request": json.dumps(request_data)})

        result = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertTrue('rows' in result)
        self.assertEqual(result['rows'], expected_rows)

    def test_group_overwrite_dynamic_charts_request(self):
        expected_rows = [{u"found_on": u"www.google.com", u"job_views": 10},
                         {u"found_on": u"www.google.de", u"job_views": 3}]
        self.populate_mongo_data()
        request_data = {"date_start": "10/18/2012 00:00:00",
                        "date_end": "10/19/2012 00:00:00",
                        "active_filters": [],
                        "report": "job-locations",
                        "group_overwrite": "found_on"}
        response = self.client.post(reverse(dynamic_chart),
                                    {"request": json.dumps(request_data)})

        result = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertTrue('rows' in result)
        self.assertEqual(result['rows'], expected_rows)

    def test_active_filter_dynamic_charts_request(self):
        expected_rows = [{u"state": u"IN", u"job_views": 9},
                         {u"state": u"MI", u"job_views": 1}]
        self.populate_mongo_data()
        request_data = {"date_start": "10/18/2012 00:00:00",
                        "date_end": "10/19/2012 00:00:00",
                        "active_filters": [{"type":"country", "value":"USA"}],
                        "report": "job-locations"}
        response = self.client.post(reverse(dynamic_chart),
                                    {"request": json.dumps(request_data)})

        result = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertTrue('rows' in result)
        self.assertEqual(result['rows'], expected_rows)

    def test_2_active_filters_dynamic_charts_request(self):
        expected_rows = [{u"city": u"Indianapolis", u"job_views": 7},
                         {u"city": u"Peru", u"job_views": 2}]
        self.populate_mongo_data()
        request_data = {"date_start": "10/18/2012 00:00:00",
                        "date_end": "10/19/2012 00:00:00",
                        "active_filters": [{"type":"country", "value":"USA"},
                                           {"type":"state", "value":"IN"}],
                        "report": "job-locations"}
        response = self.client.post(reverse(dynamic_chart),
                                    {"request": json.dumps(request_data)})

        result = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertTrue('rows' in result)
        self.assertEqual(result['rows'], expected_rows)

    def test_3_active_filters_dynamic_charts_request(self):
        expected_rows = [{u"found_on": u"www.google.com", u"job_views": 7}]
        self.populate_mongo_data()
        request_data = {"date_start": "10/18/2012 00:00:00",
                        "date_end": "10/19/2012 00:00:00",
                        "active_filters": [{"type":"country", "value":"USA"},
                                           {"type":"state", "value":"IN"},
                                           {"type":"city", "value":"Indianapolis"}],
                        "report": "job-locations"}
        response = self.client.post(reverse(dynamic_chart),
                                    {"request": json.dumps(request_data)})

        result = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertTrue('rows' in result)
        self.assertEqual(result['rows'], expected_rows)

    def test_dynamic_charts_report_info_missing_date(self):
        request_data = {"date_end": "11/28/2016 00:00:00"}
        response = self.client.post(reverse(dynamic_chart),
                                    {"request": json.dumps(request_data)})
        self.assertEqual(400, response.status_code)
        result = json.loads(response.content)
        fields = [i['field'] for i in result]
        self.assertIn('date_start', fields)

    def test_dynamic_charts_report_info_no_data(self):
        request_data = {}
        response = self.client.post(reverse(dynamic_chart),
                                    {"request": json.dumps(request_data)})
        result = json.loads(response.content)
        self.assertEqual(400, response.status_code)
        message = result[0]['message']
        self.assertEqual(message, 'No data provided.')