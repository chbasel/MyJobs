"""Tests associated with myreports views."""
import json
import os

from django.core.urlresolvers import reverse

from myjobs.tests.test_views import TestClient
from mypartners.models import ContactRecord, Partner
from mypartners.tests.factories import (ContactFactory, ContactRecordFactory,
                                        PartnerFactory, LocationFactory)
from myreports.models import Report
from myreports.tests.setup import MyReportsTestCase


class TestOverview(MyReportsTestCase):
    """Tests the reports view, which is the landing page for reports."""

    def test_available_to_staff(self):
        """Should be available to staff users."""

        response = self.client.get(reverse('overview'))

        self.assertEqual(response.status_code, 200)


class TestViewRecords(MyReportsTestCase):
    """
    Tests the `view_records` view which is used to query various models.
    """

    def setUp(self):
        super(TestViewRecords, self).setUp()
        self.client = TestClient(path='/reports/ajax/mypartners',
                                 HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.client.login_user(self.user)

        ContactRecordFactory.create_batch(
            10, partner=self.partner, contact__name='Joe Shmoe')

    def test_restricted_to_ajax(self):
        """View should only be reachable through AJAX."""

        self.client.path += '/partner'
        self.client.defaults.pop('HTTP_X_REQUESTED_WITH')
        response = self.client.post()

        self.assertEqual(response.status_code, 404)

    def test_restricted_to_post(self):
        """POST requests should raise a 404."""

        self.client.path += '/partner'
        response = self.client.get()

        self.assertEqual(response.status_code, 404)

    def test_json_output(self):
        """Test that filtering contact records through ajax works properly."""

        # records to be filtered out
        ContactRecordFactory.create_batch(10, contact__name='John Doe')

        self.client.path += '/contactrecord'
        filters = json.dumps({
            'contact': {
                'name': {
                    'icontains': 'Joe Shmoe'
                }
            }
        })
        response = self.client.post(data={'filters': filters})
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output), 10)

    def test_only_user_results_returned(self):
        """Results should only contain records user has access to."""

        # records not owned by user
        partner = PartnerFactory(name="Wrong Partner")
        ContactRecordFactory.create_batch(10, partner=partner)

        self.client.path += '/contactrecord'
        response = self.client.post()
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output), 10)

    def test_filtering_on_model(self):
        """Test the ability to filter on a model's field's."""

        # we already have one because of self.partner
        PartnerFactory.create_batch(9, name='Test Partner', owner=self.company)

        self.client.path += '/partner'
        filters = json.dumps({
            'name': {
                'icontains': 'Test Partner'
            }
        })
        response = self.client.post(data={'filters': filters})
        output = json.loads(response.content)

        # ContactRecordFactory creates 10 partners in setUp
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output), 10)

    def test_filtering_on_foreign_key(self):
        """Test the ability to filter on a model's foreign key fields."""

        PartnerFactory.create_batch(5, name='Test Partner', owner=self.company)

        ContactRecordFactory.create_batch(
            5, partner=self.partner, contact__name='Jane Doe')

        self.client.path += '/partner'
        filters = json.dumps({
            'name': {
                'icontains': 'Test Partner',
            },
            'contactrecord': {
                'contact': {
                    'name': {
                        'icontains': 'Jane Doe'
                    }
                }
            }
        })
        response = self.client.post(data={'filters': filters})
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        # We look for distinct records
        self.assertEqual(len(output), 1)

    def test_list_query_params(self):
        """Test that query parameters that are lists are parsed correctly."""

        contacts = ContactFactory.create_batch(10, partner__owner=self.company)
        pks = [contact.pk for contact in contacts[:5]]

        self.client.path += '/partner'
        filters = json.dumps({
            'contact': {
                'in': pks
            }
        })
        response = self.client.post(data={'filters': filters})
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output), 5)


class TestReportView(MyReportsTestCase):
    """
    Tests the ReportView class, which is used to create and retrieve
    reports.
    """
    def setUp(self):
        super(TestReportView, self).setUp()
        self.client = TestClient(path=reverse('reports', kwargs={
            'app': 'mypartners', 'model': 'contactrecord'}))
        self.client.login_user(self.user)

        ContactRecordFactory.create_batch(5, partner=self.partner)
        ContactRecordFactory.create_batch(
            5, contact_type='job', job_applications=1,
            partner=self.partner)
        ContactRecordFactory.create_batch(
            5, contact_type='job',
            job_hires=1, partner=self.partner)

    def test_create_report(self):
        """Test that a report model instance is properly created."""

        # create a report whose results is for all contact records in the
        # company
        response = self.client.post()
        report_name = response.content
        report = Report.objects.get(name=report_name)

        self.assertEqual(len(report.python), 15)

        # we use this in other tests
        return report_name

    def test_get_report(self):
        """Test that chart data is retreived from record results."""

        report_name = self.test_create_report()
        report = Report.objects.get(name=report_name)

        response = self.client.get(data={'id': report.pk})
        data = json.loads(response.content)

        # check contact record stats
        for key in ['applications', 'hires', 'communications', 'emails']:
            self.assertEqual(data[key], 5)

        # check contact stats
        self.assertEqual(data['contacts'][0]['records'], 5)
        self.assertEqual(data['contacts'][0]['referrals'], 10)

    def test_reports_exclude_archived(self):
        """
        Test that reports exclude archived records as appropriate. This
        includes non-archived records associated with archived records.
        """
        self.client.path = reverse('view_records', kwargs={
            'app': 'mypartners', 'model': 'contactrecord'})

        response = self.client.post(HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        content = json.loads(response.content)
        self.assertEqual(len(content), 15)

        ContactRecord.objects.last().archive()

        # Archiving one communication record should result in one fewer entry
        # in the returned json.
        response = self.client.post(HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        content = json.loads(response.content)
        self.assertEqual(len(content), 14)

        Partner.objects.last().archive()

        # Archiving the partner governing these communication records should
        # exclude all of them from the returned json even if they aren't
        # archived.
        response = self.client.post(HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        content = json.loads(response.content)
        self.assertEqual(len(content), 0)


class TestDownloads(MyReportsTestCase):
    """Tests the reports view."""

    def setUp(self):
        super(TestDownloads, self).setUp()
        self.client = TestClient(path=reverse('downloads'),
                                 HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.client.login_user(self.user)

        ContactRecordFactory.create_batch(10, partner__owner=self.company)

    def test_column_order(self):
        """Tests that column order is preserved"""

        # create a report whose results is for all contact records in the
        # company
        response = self.client.post(
            path=reverse('reports', kwargs={
                'app': 'mypartners', 'model': 'contactrecord'}))

        report_name = response.content
        report = Report.objects.get(name=report_name)
        report.values = json.dumps(['partner', 'contact name', 'contact_type'])
        report.save()

        response = self.client.get(data={'id': report.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['columns'].items()[:3],
                         [('Partner', True), ('Contact Name', True),
                          ('Communication Type', True)])

    def test_blacklisted_columns(self):
        """Test that blacklisted columns aren't visible."""
        blacklist = ['pk', 'approval_status']
        response = self.client.post(
            path=reverse('reports', kwargs={
                'app': 'mypartners', 'model': 'contactrecord'}),
            data={'values': ['partner', 'contact__name', 'contact_type']})

        report_name = response.content
        report = Report.objects.get(name=report_name)

        response = self.client.get(data={'id': report.id})
        self.assertFalse(
            set(response.context['columns']).intersection(blacklist))


class TestDownloadReport(MyReportsTestCase):
    """Tests that reports can be downloaded."""

    def setUp(self):
        super(TestDownloadReport, self).setUp()
        self.client = TestClient(path=reverse('download_report'))
        self.client.login_user(self.user)

        ContactRecordFactory.create_batch(5, partner__owner=self.company)
        ContactRecordFactory.create_batch(
            5, contact_type='job', job_applications=1,
            partner__owner=self.company)
        ContactRecordFactory.create_batch(
            5, contact_type='job',
            job_hires=1, partner__owner=self.company)

    def test_download_csv(self):
        """Test that a report can be downloaded in CSV format."""

        # create a report whose results is for all contact records in the
        # company
        response = self.client.post(path=reverse('reports', kwargs={
            'app': 'mypartners', 'model': 'contactrecord'}))
        report_name = response.content
        report = Report.objects.get(name=report_name)
        python = report.python

        # download the report
        response = self.client.get(data={
            'id': report.pk,
            'values': ['contact', 'contact_email', 'contact_phone']})

        self.assertEqual(response['Content-Type'], 'text/csv')

        # specifying export values shouldn't modify the underlying report
        self.assertEqual(len(python[0].keys()), len(report.python[0].keys()))


class TestRegenerate(MyReportsTestCase):
    """Tests the reports can be regenerated."""

    def setUp(self):
        super(TestRegenerate, self).setUp()
        self.client = TestClient(path=reverse('reports', kwargs={
            'app': 'mypartners', 'model': 'contactrecord'}))
        self.client.login_user(self.user)

        ContactRecordFactory.create_batch(10, partner__owner=self.company)

    def test_regenerate(self):
        # create a new report
        response = self.client.post(
            path=reverse('reports', kwargs={
                'app': 'mypartners', 'model': 'contactrecord'}))

        report_name = response.content
        report = Report.objects.get(name=report_name)

        response = self.client.get(data={'id': report.id})
        self.assertEqual(response.status_code, 200)

        # remove report results and ensure we can still get a reasonable
        # response
        report.results.delete()
        report.save()
        self.assertFalse(report.results)

        response = self.client.get(data={'id': report.id})
        self.assertEqual(response.status_code, 200)

        # regenerate results and ensure they are the same as the original
        response = self.client.get(path=reverse('regenerate'), data={
            'id': report.pk})
        report = Report.objects.get(name=report_name)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(report.results)

        # regenerate report without deleting the report prior
        # see if it overwrites other report.
        results = report.results
        response = self.client.get(path=reverse('regenerate'), data={
            'id': report.pk})
        report = Report.objects.get(name=report_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(results.name, report.results.name)

    def test_regenerating_missing_file(self):
        """Tests that a report can be regenerated when file is missing."""

        # create a new report
        response = self.client.post(
            path=reverse('reports', kwargs={
                'app': 'mypartners', 'model': 'contactrecord'}))

        report_name = response.content
        report = Report.objects.get(name=report_name)

        # report should have results
        self.assertTrue(report.results)

        # delete physical file and ensure that json reflects the missing link
        os.remove(report.results.file.name)
        report = Report.objects.get(pk=report.pk)
        self.assertEqual(report.json, u'{}')
        self.assertEqual(report.python, {})

        # regenerate the report even though the file is physically missing
        report.regenerate()
        self.assertTrue(report.results)


class TestReportsApi(MyReportsTestCase):
    def setUp(self):
        super(TestReportsApi, self).setUp()
        ContactFactory.create(
            name="a", email="a@example.com",
            partner=self.partner,
            locations=[
                LocationFactory.create(
                    city="Chicago",
                    state="IL"),
                LocationFactory.create(
                    city="Champaign",
                    state="IL"),
                ])

    def test_reporting_types_api_fail_get(self):
        """Try an invalid method on reporting types."""
        resp = self.client.get(reverse('reporting_types_api'))
        self.assertEquals(405, resp.status_code)

    def test_reporting_types_api(self):
        """Test that we get only active reporting types."""
        resp = self.client.post(reverse('reporting_types_api'))
        data = json.loads(resp.content)['reporting_type']
        self.assertEquals(1, len(data))
        self.assertEquals('PRM', data['1']['name'])
        self.assertEquals('PRM Reports', data['1']['description'])

    def test_report_types_api_fail_get(self):
        """Try an invalid method on report types."""
        resp = self.client.get(reverse('report_types_api'))
        self.assertEquals(405, resp.status_code)

    def test_report_types_api(self):
        """Test that we get only active report types."""
        resp = self.client.post(reverse('report_types_api'),
                                data={'reporting_type_id': '1'})
        data = json.loads(resp.content)['report_type']
        self.assertEquals(3, len(data))
        self.assertEquals("Partners", data['1']['name'])
        self.assertEquals("Partners Report", data['1']['description'])
        self.assertEquals("Contacts", data['2']['name'])
        self.assertEquals("Contacts Report", data['2']['description'])
        self.assertEquals("Communication Records", data['3']['name'])
        self.assertEquals("Communication Records Report",
                          data['3']['description'])

    def test_data_types_api(self):
        """Test that we get only active data types."""
        resp = self.client.post(reverse('data_types_api'),
                                data={'report_type_id': '2'})
        data = json.loads(resp.content)['data_type']
        self.assertEquals(1, len(data))
        self.assertEquals("Unaggregated", data['3']['name'])
        self.assertEquals("Unaggregated Data Type", data['3']['description'])

    def test_presentation_api(self):
        """Test that we get only active presentation types."""
        resp = self.client.post(reverse('presentation_types_api'),
                                data={'report_type_id': '2',
                                      'data_type_id': '3'})
        data = json.loads(resp.content)['report_presentation']
        self.assertEquals(1, len(data))
        self.assertEquals("Contact CSV", data['3']['name'])

    def test_filters_api(self):
        """Test that we get descriptions of available filters."""
        resp = self.client.post(reverse('filters_api'),
                                data={'rp_id': '3'})
        result = json.loads(resp.content)
        expected_keys = set(['filters', 'help'])
        self.assertEquals(expected_keys, set(result.keys()))

    def test_help_api(self):
        """Test the dynamic report help api.

        We should get back suggestions based on existing input.
        """
        resp = self.client.post(
            reverse('help_api'),
            data={
                'rp_id': 3,
                'filter': json.dumps({'locations': {'state': 'IL'}}),
                'field': 'city',
                'partial': 'i',
            })
        self.assertEquals(200, resp.status_code)
        result = json.loads(resp.content)
        expected_result = [
            {'display': 'Chicago', 'key': 'Chicago'},
            {'display': 'Champaign', 'key': 'Champaign'},
        ]
        self.assertEqual(expected_result, result)


class TestDynamicReports(MyReportsTestCase):
    def test_dynamic_report(self):
        """Create some test data, run, list, and download a report."""
        self.client.login_user(self.user)

        partner = PartnerFactory(owner=self.company)
        for i in range(0, 10):
            # unicode here to push through report generation/download
            ContactFactory.create(
                name=u"name-%s \u2019" % i,
                partner=partner)

        resp = self.client.post(
            reverse('run_dynamic_report'),
            data={
                'rp_id': 3,
                'name': 'The Report',
            })
        self.assertEqual(200, resp.status_code)
        report_id = json.loads(resp.content)['id']

        resp = self.client.get(reverse('list_dynamic_reports'))
        self.assertEqual(200, resp.status_code)
        self.assertEqual(
            {'reports': [
                {'id': report_id, 'name': 'The Report'},
            ]},
            json.loads(resp.content))

        resp = self.client.get(reverse('download_dynamic_report'),
                               {'id': report_id})
        self.assertEquals(200, resp.status_code)
        lines = resp.content.splitlines()
        self.assertEquals(11, len(lines))
        first_found_name = lines[1].split(',')[0]
        expected_name = u'name-0 \u2019'.encode('utf-8')
        self.assertEqual(expected_name, first_found_name)

    def test_dynamic_report_with_filter(self):
        """Create some test data, run filtered, and download a report."""
        self.client.login_user(self.user)

        partner = PartnerFactory(owner=self.company)
        for i in range(0, 10):
            location = LocationFactory.create(
                city="city-%s" % i)
            ContactFactory.create(
                name="name-%s" % i,
                partner=partner,
                locations=[location])

        resp = self.client.post(
            reverse('run_dynamic_report'),
            data={
                'rp_id': 3,
                'name': 'The Report',
                'filter': json.dumps({
                    'locations': {
                        'city': 'city-2',
                    },
                }),
            })
        self.assertEqual(200, resp.status_code)
        report_id = json.loads(resp.content)['id']

        resp = self.client.get(reverse('download_dynamic_report'),
                               {'id': report_id})
        self.assertEquals(200, resp.status_code)
        lines = resp.content.splitlines()
        self.assertEquals(2, len(lines))
        first_found_name = lines[1].split(',')[0]
        expected_name = 'name-2'
        self.assertEqual(expected_name, first_found_name)
