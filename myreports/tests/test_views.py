"""Tests associated with myreports views."""
import json
import os
from datetime import datetime

from django.core.urlresolvers import reverse

from myjobs.tests.test_views import TestClient
from mypartners.models import ContactRecord, Partner
from mypartners.tests.factories import (ContactFactory, ContactRecordFactory,
                                        PartnerFactory, LocationFactory,
                                        TagFactory)
from myreports.models import Report, ReportPresentation, PresentationType
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
            5, contact_type='job',
            job_applications="1", job_interviews="0", job_hires="0",
            partner=self.partner)
        ContactRecordFactory.create_batch(
            5, contact_type='job',
            job_applications="0", job_interviews="0", job_hires="1",
            partner=self.partner)

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
        self.assertEquals("unaggregated", data['3']['name'])
        self.assertEquals("Unaggregated", data['3']['description'])

    def test_presentation_api(self):
        """Test that we get only active presentation types."""
        resp = self.client.post(reverse('presentation_types_api'),
                                data={'report_type_id': '2',
                                      'data_type_id': '3'})
        data = json.loads(resp.content)['report_presentation']
        names = set(v['name'] for v in data.values())
        expected_names = set(["Contact CSV", "Contact Excel Spreadsheet"])
        self.assertEquals(expected_names, names)

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
    def setUp(self):
        super(TestDynamicReports, self).setUp()

        self.json_pass = PresentationType.objects.get(
            presentation_type='json_pass')
        self.json_pass.is_active = True
        self.json_pass.save()

    def find_report_presentation(
            self, datasource, presentation_type, data_type='unaggregated'):
        return ReportPresentation.objects.get(
            is_active=True,
            configuration__is_active=True,
            presentation_type__is_active=True,
            report_data__report_type__datasource=datasource,
            report_data__data_type__data_type=data_type,
            presentation_type__presentation_type=presentation_type)

    def test_dynamic_contacts_report(self):
        """Create some test data, run, list, and download a contacts report."""
        self.client.login_user(self.user)

        partner = PartnerFactory(owner=self.company)
        for i in range(0, 10):
            # unicode here to push through report generation/download
            ContactFactory.create(
                name=u"name-%s \u2019" % i,
                partner=partner)

        report_presentation = self.find_report_presentation(
            'contacts',
            'json_pass')

        resp = self.client.post(
            reverse('run_dynamic_report'),
            data={
                'rp_id': report_presentation.pk,
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

        response_data = json.loads(resp.content)
        self.assertEquals(10, len(response_data['records']))

        first_found_name = response_data['records'][0]['name']
        expected_name = u'name-0 \u2019'
        self.assertEqual(expected_name, first_found_name)

    def test_dynamic_partners_report(self):
        """Create some test data, run, list, and download a partners report."""
        self.client.login_user(self.user)

        for i in range(0, 20):
            # unicode here to push through report generation/download
            PartnerFactory(
                owner=self.company,
                name=u"partner-%s \u2019" % i)

        report_presentation = self.find_report_presentation(
            'partners',
            'json_pass')

        resp = self.client.post(
            reverse('run_dynamic_report'),
            data={
                'rp_id': report_presentation.pk,
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
        response_data = json.loads(resp.content)
        self.assertEquals(21, len(response_data['records']))

        last_found_name = response_data['records'][-1]['name']
        expected_name = u'partner-19 \u2019'
        self.assertEqual(expected_name, last_found_name)

    def test_dynamic_comm_records_report(self):
        """Create some test data, run, list, and download a commrec report."""
        self.client.login_user(self.user)

        partner = PartnerFactory(owner=self.company)
        contact = ContactFactory.create(name='somename', partner=partner)

        for i in range(0, 20):
            # unicode here to push through report generation/download
            ContactRecordFactory(
                partner=partner,
                contact=contact,
                subject=u"subject-%s \u2019" % i)

        report_presentation = self.find_report_presentation(
            'comm_records',
            'json_pass')

        resp = self.client.post(
            reverse('run_dynamic_report'),
            data={
                'rp_id': report_presentation.pk,
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
        response_data = json.loads(resp.content)
        self.assertEquals(20, len(response_data['records']))

        last_subject = response_data['records'][-1]['subject']
        expected_subject = u'subject-19 \u2019'
        self.assertEqual(expected_subject, last_subject)

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

        report_presentation = self.find_report_presentation(
            'contacts',
            'json_pass')

        resp = self.client.post(
            reverse('run_dynamic_report'),
            data={
                'rp_id': report_presentation.pk,
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
        response_data = json.loads(resp.content)
        self.assertEquals(1, len(response_data['records']))

        found_name = response_data['records'][0]['name']
        expected_name = u'name-2'
        self.assertEqual(expected_name, found_name)

    def test_dynamic_partners_report_csv(self):
        """Run a report through the csv presentation type.

        Just make sure the document loads.
        """
        self.client.login_user(self.user)

        for i in range(0, 20):
            # unicode here to push through report generation/download
            PartnerFactory(
                owner=self.company,
                name=u"partner-%s \u2019" % i)

        report_presentation = self.find_report_presentation(
            'partners',
            'csv')

        resp = self.client.post(
            reverse('run_dynamic_report'),
            data={
                'rp_id': report_presentation.pk,
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
        self.assertIn('The_Report.csv', resp['content-disposition'])
        self.assertIn('text/csv', resp['content-type'])

    def test_dynamic_partners_report_xlsx(self):
        """Run a report through the xlsx presentation type.

        Just make sure the document loads.
        """
        self.client.login_user(self.user)

        for i in range(0, 20):
            # unicode here to push through report generation/download
            PartnerFactory(
                owner=self.company,
                name=u"partner-%s \u2019" % i)

        report_presentation = self.find_report_presentation(
            'partners',
            'xlsx')

        resp = self.client.post(
            reverse('run_dynamic_report'),
            data={
                'rp_id': report_presentation.pk,
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
        self.assertIn('The_Report.xlsx', resp['content-disposition'])
        self.assertIn('application/vnd.', resp['content-type'])

    def test_missing_report_name(self):
        """Returns an error if the report name is missing."""
        report_presentation = self.find_report_presentation(
            'partners',
            'json_pass')

    def test_dynamic_partners_report_comm_per_month(self):
        """Run the comm_rec per month per partner report."""
        self.client.login_user(self.user)

        partner = PartnerFactory(owner=self.company)
        partner.tags.add(TagFactory.create(name="this"))
        contact = ContactFactory.create(name='somename', partner=partner)

        for i in range(0, 20):
            # unicode here to push through report generation/download
            ContactRecordFactory(
                partner=partner,
                contact=contact,
                date_time=datetime(2015, 2, 4),
                subject=u"subject-%s \u2019" % i)

        report_presentation = self.find_report_presentation(
            'partners',
            'json_pass',
            data_type="count_comm_rec_per_month")

        resp = self.client.post(
            reverse('run_dynamic_report'),
            data={
                'rp_id': report_presentation.pk,
                'name': 'The Report',
                'filter': json.dumps({
                    'tags': [['this']],
                }),
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
        response_data = json.loads(resp.content)
        self.assertEquals(12, len(response_data['records']))
        january = response_data['records'][0]
        self.assertEqual('1', january['month'])
        self.assertEqual('0', january['comm_rec_count'])
        february = response_data['records'][1]
        self.assertEqual('2', february['month'])
        self.assertEqual('20', february['comm_rec_count'])

    def test_default_report_name(self):
        """Returns a nice timestampy default report name."""
        report_presentation = self.find_report_presentation(
            'partners',
            'xlsx')
        post_data = {'report_presentation_id': report_presentation.pk}
        resp = self.client.post(reverse('get_default_report_name'), post_data)
        self.assertEqual(200, resp.status_code)
        doc = json.loads(resp.content)
        self.assertIn('name', doc)
        self.assertRegexpMatches(doc['name'], '^\d{4}-')

    def test_default_report_name_error(self):
        """Returns a 400 on missing parameter."""
        resp = self.client.post(reverse('get_default_report_name'), {})
        self.assertEqual(400, resp.status_code)
        doc = json.loads(resp.content)
        field_keys = {r['field'] for r in doc}
        self.assertIn('report_presentation_id', field_keys)
