import json

from myjobs.tests.setup import MyJobsBase
import myreports.models as myreports_models

from django.core.urlresolvers import reverse

from analytics.api import get_available_analytics, get_report_info


class TestApi(MyJobsBase):
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
