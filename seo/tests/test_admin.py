from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

from myjobs.models import User, Activity
from myjobs.tests.factories import RoleFactory
from seo.tests import factories
from seo.models import SeoSite, BusinessUnit
from seo.tests.factories import CompanyFactory
from seo.tests.setup import DirectSEOBase

from bs4 import BeautifulSoup
from djcelery.models import TaskState
from django.test.utils import override_settings
from datetime import datetime
import pytz


class SeoAdminTestCase(DirectSEOBase):
    def setUp(self):
        super(SeoAdminTestCase, self).setUp()
        self.password = 'imbatmancalifornia'
        self.user = User.objects.create_superuser(password=self.password,
                                                  email='bc@batyacht.com')
        self.user.save()
        self.client.login(email=self.user.email,
                          password=self.password)

    def test_seo_site_can_be_child(self):
        """
            Ensure SEO Site can be added as a child via the admin form
        """
        parent_seo_site = factories.SeoSiteFactory()
        group_for_new_site = factories.GroupFactory()
        resp = self.client.post(reverse('admin:seo_seosite_add'),
                                {'domain':'newdomain_testnormal',
                                'name':'new_name',
                                'group':group_for_new_site.pk,
                                'postajob_filter_type':'this site only',
                                'parent_site':parent_seo_site.pk})
        self.assertEqual(resp.status_code, 302) # redirect on successful add
        self.assertFalse("field-parent_site errors" in resp)
        created_site = SeoSite.objects.get(domain='newdomain_testnormal')
        self.assertEqual(created_site.parent_site, parent_seo_site)

    def test_seo_site_cannot_be_child_of_child(self):
        """
            Ensure a child SEO Site cannot be a parent via the admin form
        """
        parent_seo_site = factories.SeoSiteFactory()
        child_seo_site = factories.SeoSiteFactory()
        child_seo_site.parent_site = parent_seo_site
        child_seo_site.save()
        group_for_new_site = factories.GroupFactory()
        resp = self.client.post(reverse('admin:seo_seosite_add'),
                                {'domain':'newdomain_testnochildchild',
                                'name':'new_name',
                                'group':group_for_new_site.pk,
                                'postajob_filter_type':'this site only',
                                'parent_site':child_seo_site.pk})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "field-parent_site errors")
        with self.assertRaises(ObjectDoesNotExist):
            created_site = SeoSite.objects.get(domain='newdomain_testnochildchild')

    def test_seo_site_parent_cannot_become_child(self):
        """
            Ensure a child SEO Site cannot be a parent via the admin form
        """
        super_parent_seo_site = factories.SeoSiteFactory()
        parent_seo_site = factories.SeoSiteFactory()
        child_seo_site = factories.SeoSiteFactory()
        child_seo_site.parent_site = parent_seo_site
        child_seo_site.save()
        resp = self.client.post(reverse('admin:seo_seosite_change',args=(parent_seo_site.pk,)),
                                {'domain':'newdomain_testparentnochildbecome',
                                'name':parent_seo_site.name,
                                'group':parent_seo_site.group.pk,
                                'postajob_filter_type':parent_seo_site.postajob_filter_type,
                                'parent_site':super_parent_seo_site.pk})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "field-parent_site errors")
        parent_site_refresh = SeoSite.objects.get(pk = parent_seo_site.pk)
        self.assertEqual(parent_site_refresh.parent_site, None)

    def test_company_admin_role_table(self):
        """
        Tests the "User Roles" section of the Company admin.
        """
        def make_request_and_initial_checks():
            """
            Both tests in the parent function involve making a GET request,
            parsing the HTML, and doing a small amount of checking.
            """
            response = self.client.get(reverse('admin:seo_company_change',
                                               args=(company.pk, )))
            soup = BeautifulSoup(response.content)
            user_roles = soup.find('div', {'class': 'field-user_roles'})
            self.assertTrue(user_roles, "Expected to find a div with class "
                            "'field-user_roles' but did not.")
            return user_roles.find('table').text

        company = CompanyFactory()
        role = RoleFactory(company=company)
        role.activities = Activity.objects.all()

        # Test once with no roles assigned.
        table_text = make_request_and_initial_checks()
        self.assertFalse(table_text, "User roles table should be empty when "
                         "no users have roles.")

        self.user.roles.add(role)

        # Test again with a role assigned to a user.
        table_text = make_request_and_initial_checks()
        self.assertTrue(table_text, "User roles table should contain data "
                        "when there are users with roles assigned.")
        for text in [self.user.email, role.name]:
            self.assertTrue(text in table_text, 'Expected "%s" to be in '
                            'table text but it was not.' % (text, ))


class DJCeleryAdminTestCase(DirectSEOBase):
    fixtures= ["countries.json"]

    def setUp(self):
        super(type(self), self).setUp()
        # User credentials
        self.password = 'imbatmancalifornia'
        self.user = User.objects.create_superuser(password=self.password,
                                                  email='bc@batyacht.com')
        self.user.save()
        self.client.login(email=self.user.email,
                          password=self.password)

        # Task to resend
        self.id = 25506
        self.date = datetime(year=2015, month=1, day=1, hour=1, minute=1, second=1, tzinfo=pytz.utc)
        self.bu = BusinessUnit(id=self.id, date_updated=self.date, date_crawled=self.date)
        self.bu.save()
        self.etl_to_solr = TaskState(state="test", task_id="testing",
                                     name="priority_etl_to_solr", tstamp=datetime.now(),
                                     args="""(u'442e8eab-a4d8-4c49-9ee1-c408c509c1ca', u'25506', u'Penske')""",
                                     kwargs="{}")
        self.etl_to_solr.save()

    @override_settings(CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
    def test_requeue_etl_task(self):
        url = "http://www.my.jobs/admin/djcelery/taskstate/"
        data = {'action': 'resend_task',
                '_selected_action': [unicode(self.etl_to_solr.pk)]}

        self.assertEqual(self.bu.date_updated, self.date)
        self.client.post(url, data)
        bu = BusinessUnit.objects.get(pk=self.id)
        self.assertNotEqual(bu.date_updated, self.date)
