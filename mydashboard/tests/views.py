import pysolr

from bs4 import BeautifulSoup
from datetime import timedelta

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import TestCase

from mydashboard.models import CompanyUser
from mydashboard.tests.factories import CompanyFactory, CompanyUserFactory, MicrositeFactory
from myjobs.tests.views import TestClient
from myjobs.tests.factories import UserFactory
from myprofile.tests.factories import (PrimaryNameFactory,
                                       SecondaryEmailFactory,
                                       EducationFactory, LicenseFactory,
                                       AddressFactory, TelephoneFactory,
                                       EmploymentHistoryFactory)
from mysearches.models import SavedSearch
from mysearches.tests.factories import SavedSearchFactory
from tasks import add_to_solr_task, delete_from_solr_task

SEARCH_OPTS = ['django', 'python', 'programming']


class MyDashboardViewsTests(TestCase):
    def setUp(self):
        self.staff_user = UserFactory()
        group = Group.objects.get(name=CompanyUser.GROUP_NAME)
        self.staff_user.groups.add(group)
        self.staff_user.save()

        self.company = CompanyFactory()
        self.company.save()
        self.admin = CompanyUserFactory(user=self.staff_user,
                                        company=self.company)
        self.admin.save()
        self.microsite = MicrositeFactory(company=self.company)
        self.microsite.save()

        self.client = TestClient()
        self.client.login_user(self.staff_user)

        self.candidate_user = UserFactory(email="example@example.com")
        SavedSearchFactory(user=self.candidate_user,
                           url='http://test.jobs/search?q=django',
                           label='test Jobs')
        self.candidate_user.save()

        for i in range(5):
            # Create 5 new users
            user = UserFactory(email='example%s@example.com' % i)
            for search in SEARCH_OPTS:
                # Create 15 new searches and assign three per user
                SavedSearchFactory(user=user,
                                   url='http://test.jobs/search?q=%s' % search,
                                   label='%s Jobs' % search)
        add_to_solr_task('http://127.0.0.1:8983/solr/myjobs_test/')

    def tearDown(self):
        solr = pysolr.Solr('http://127.0.0.1:8983/solr/myjobs_test/')
        solr.delete(q='*:*')

    def test_number_of_searches_and_users_is_correct(self):
        response = self.client.post(
            reverse('dashboard')+'?company='+str(self.company.id),
            {'microsite': 'test.jobs'})
        soup = BeautifulSoup(response.content)
        # 6 users total, two rows per search
        self.assertEqual(len(soup.select('#row-link-table tr')), 12)

        old_search = SavedSearch.objects.all()[0]
        old_search.created_on -= timedelta(days=31)
        old_search.save()

        response = self.client.post(
            reverse('dashboard')+'?company='+str(self.company.id),
            {'microsite': 'test.jobs'})
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select('#row-link-table tr')), 12)

    def test_facets(self):
        self.education = EducationFactory(user=self.candidate_user)
        self.adr = AddressFactory(user=self.candidate_user)
        self.employment = EmploymentHistoryFactory(user=self.candidate_user)
        self.license = LicenseFactory(user=self.candidate_user)
        self.candidate_user.save()
        add_to_solr_task('http://127.0.0.1:8983/solr/myjobs_test/')

        country_str = '<li><a href="http://testserver/candidates/view?company=1&amp;location={country}">(1) {country}</a></li>'
        edu_str = '<li><a href="http://testserver/candidates/view?company=1&amp;education={education}">(1)'
        license_str = '<li><a href="http://testserver/candidates/view?company=1&amp;license=Name">(1) {license_name}</a></li>'

        country_str = country_str.format(country=self.adr.country_code)
        edu_str = edu_str.format(education=self.education.education_level_code)
        license_str = license_str.format(license_name=self.license.license_name)

        q = '?company={company}'
        q = q.format(company=str(self.company.id))
        response = self.client.post(reverse('dashboard')+q)

        self.assertIn(country_str, response.content)
        self.assertIn(edu_str, response.content)
        self.assertIn(license_str, response.content)

    def test_filters(self):
        adr = AddressFactory(user=self.candidate_user)
        self.candidate_user.save()
        add_to_solr_task('http://127.0.0.1:8983/solr/myjobs_test/')

        country_str = '<li><a href="http://testserver/candidates/view?company=1&amp;location={country}">(1) {country}</a></li>'
        country_filter_str = '<a class="applied-filter" href="http://testserver/candidates/view?company=1"><span>&#10006;</span> {country}</a><br>'
        region_str = '<li><a href="http://testserver/candidates/view?company=1&amp;location={country}-{region}">(1) {region}</a></li>'
        region_filter_str = '<a class="applied-filter" href="http://testserver/candidates/view?company=1&amp;location={country}"><span>&#10006;</span> {region}</a><br>'
        city_str = '<li><a href="http://testserver/candidates/view?company=1&amp;location={country}-{region}-{city}">(1) {city}</a></li>'
        city_filter_str = '<a class="applied-filter" href="http://testserver/candidates/view?company=1&amp;location={country}-{region}"><span>&#10006;</span> {city}</a><br>'

        country_str = country_str.format(country=adr.country_code)
        country_filter_str = country_filter_str.format(country=adr.country_code)
        region_str = region_str.format(country=adr.country_code,
                                       region=adr.country_sub_division_code)
        region_filter_str = region_filter_str.format(region=adr.country_sub_division_code,
                                                     country=adr.country_code)
        city_str = city_str.format(country=adr.country_code,
                                   region=adr.country_sub_division_code,
                                   city=adr.city_name)
        city_filter_str = city_filter_str.format(country=adr.country_code,
                                                 region=adr.country_sub_division_code,
                                                 city=adr.city_name)

        q = '?company={company}'
        q = q.format(company=str(self.company.id))
        response = self.client.post(reverse('dashboard')+q)
        self.assertIn(country_str, response.content)

        q = '?company={company}&location={country}'
        q = q.format(company=str(self.company.id), country=adr.country_code)
        response = self.client.post(reverse('dashboard')+q)
        self.assertIn(country_filter_str, response.content)
        self.assertIn(region_str, response.content)

        q = '?company={company}&location={country}-{region}'
        q = q.format(company=str(self.company.id), country=adr.country_code,
                     region=adr.country_sub_division_code)
        response = self.client.post(reverse('dashboard')+q)
        self.assertIn(region_filter_str, response.content)
        self.assertIn(city_str, response.content)

        q = '?company={company}&location={country}-{region}-{city}'
        q = q.format(company=str(self.company.id), country=adr.country_code,
                     region=adr.country_sub_division_code,
                     city=adr.city_name)
        response = self.client.post(reverse('dashboard')+q)
        self.assertIn(city_filter_str, response.content)

    # Tests to see if redirect from /candidates/ goes to candidates/view/
    def test_redirect_to_candidates_views_default_page(self):
        response = self.client.post('/candidates/')

        # response returns HttpResponsePermanentRedirect which returns a 301
        # status code instead of the normal 302 redirect status code
        self.assertRedirects(response, '/candidates/view/', status_code=301,
                             target_status_code=200)

        response = self.client.post(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        company_name = soup.find('h1')
        company_name = company_name.next

        self.assertEqual(company_name, self.company.name)

    # Eventually these opted-in/out will be changed to
    # track if user is part of company's activity feed
    def test_candidate_has_opted_in(self):
        response = self.client.post(
            reverse('candidate_information',
                    )+'?company='+str(self.company.id)+'&user='+str(
                        self.candidate_user.id))

        self.assertEqual(response.status_code, 200)

    def test_candidate_has_opted_out(self):
        self.candidate_user.opt_in_employers = False
        self.candidate_user.save()

        response = self.client.post(
            reverse('candidate_information',
                    )+'?company='+str(self.company.id)+'&user='+str(
                        self.candidate_user.id))
        self.assertEqual(response.status_code, 404)

    def test_candidate_page_load_with_profileunits_and_activites(self):
        # Building User with ProfileUnits
        self.name = PrimaryNameFactory(user=self.candidate_user)
        self.second_email = SecondaryEmailFactory(user=self.candidate_user)
        self.education = EducationFactory(user=self.candidate_user)
        self.address = AddressFactory(user=self.candidate_user)
        self.telephone = TelephoneFactory(user=self.candidate_user)
        self.employment = EmploymentHistoryFactory(user=self.candidate_user)
        self.candidate_user.save()

        response = self.client.post(
            reverse('candidate_information',
                    )+'?company='+str(self.company.id)+'&user='+str(
                        self.candidate_user.id))

        soup = BeautifulSoup(response.content)
        titles = soup.find('div', {'id': 'candidate-content'}).findAll(
            'a', {'class': 'accordion-toggle'})
        info = soup.find('div', {'id': 'candidate-content'}).findAll('li')

        self.assertEqual(len(titles), 6)
        self.assertEqual(len(info), 16)
        self.assertEqual(response.status_code, 200)

    def test_candidate_page_load_without_profileunits_with_activites(self):
        response = self.client.post(
            reverse('candidate_information',
                    )+'?company='+str(self.company.id)+'&user='+str(
                        self.candidate_user.id))

        soup = BeautifulSoup(response.content)
        titles = soup.find('div', {'id': 'candidate-content'}).findAll(
            'a', {'class': 'accordion-toggle'})
        info = soup.find('div', {'id': 'candidate-content'}).findAll('li')

        self.assertEqual(len(titles), 1)
        self.assertEqual(len(info), 3)
        self.assertEqual(response.status_code, 200)

    def test_candidate_page_load_without_profileunits_and_activites(self):
        saved_search = SavedSearch.objects.get(user=self.candidate_user)
        saved_search.delete()
        response = self.client.post(
            reverse('candidate_information',
                    )+'?company='+str(self.company.id)+'&user='+str(
                        self.candidate_user.id))

        soup = BeautifulSoup(response.content)
        info = soup.find('div', {'id': 'candidate-content'})

        self.assertFalse(info)
        self.assertEqual(response.status_code, 404)

    def test_export_csv(self):
        response = self.client.post(
            reverse('export_candidates')+'?company=' +
            str(self.company.id)+'&ex-t=csv')
        self.assertTrue(response.content)
        self.assertEqual(response.status_code, 200)

    def test_export_pdf(self):
        response = self.client.post(
            reverse('export_candidates')+'?company=' +
            str(self.company.id)+'&ex-t=pdf')
        self.assertTrue(response.content.index('PDF'))
        self.assertEqual(response.templates[0].name,
                         'mydashboard/export/candidate_listing.html')
        self.assertEqual(response.status_code, 200)

    def test_export_xml(self):
        response = self.client.post(
            reverse('export_candidates')+'?company=' +
            str(self.company.id)+'&ex-t=xml')
        self.assertTrue(response.content.index('candidates'))
        self.assertEqual(response.status_code, 200)

    def test_export_json(self):
        response = self.client.post(
            reverse('export_candidates')+'?company=' +
            str(self.company.id)+'&ex-t=json')
        self.assertTrue(response.content.index('candidates'))
        self.assertEqual(response.status_code, 200)
