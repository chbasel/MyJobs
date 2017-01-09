#  -*- coding: utf-8 -*-
from django.conf import settings

from myjobs.models import User
from seo.tests import factories
from seo.models import SeoSite
from setup import DirectSEOBase
import thread_manager


class SiteTestCase(DirectSEOBase):
    """
        This test case is intended to verify the context processors are being
        properly run and the values needed are being added to the context.
    """
    def setUp(self):
        super(SiteTestCase, self).setUp()
        SeoSite.objects.all().delete()
        self.site = factories.SeoSiteFactory(id=1)
        settings.SITE = self.site
        thread_manager.set('SITE_ID', self.site.pk)
        self.configuration = factories.ConfigurationFactory(status=2)
        self.configuration.save()
        self.site.configurations.clear()
        self.site.configurations.add(self.configuration)

    def tearDown(self):
        super(SiteTestCase, self).tearDown()
        self.site.delete()
        self.configuration.delete()
        try:
            self.user.delete()
            self.client.logout()
        except:
            pass

    def setup_superuser(self):
        self.password = 'imbatmancalifornia'
        self.user = User.objects.create_superuser(password=self.password,
                                                  email='bc@batyacht.com')
        self.user.save()
        self.client.login(email=self.user.email,
                          password=self.password)

    def test_site_config_context(self):
        """
            Ensure the site_config context variable is populated
        """
        resp = self.client.get("/")
        self.assertEqual(resp.context['site_config'],self.configuration)

    def test_domain_switching_for_staff_context(self):
        self.setup_superuser()
        another_site = factories.SeoSiteFactory(id=2)
        another_site.domain = 'thisisatest'
        another_site.save()
        # create and test config for status 1 (non staff fallback)
        configuration_status_1 = factories.ConfigurationFactory(status=1)
        configuration_status_1.save()
        another_site.configurations.add(configuration_status_1)
        resp = self.client.get("/?domain=thisisatest")
        self.assertEqual(resp.context['site_config'],configuration_status_1)
        # create and test config for status 2 (non staff primary page)
        configuration_status_2 = factories.ConfigurationFactory(status=2)
        another_site.configurations.add(configuration_status_2)
        resp = self.client.get("/?domain=thisisatest")
        self.assertNotEqual(resp.context['site_config'],configuration_status_1)
        self.assertEqual(resp.context['site_config'],configuration_status_2)

    def test_parent_domain_context_variable(self):
        parent_site = factories.SeoSiteFactory()
        self.site.parent_site = parent_site
        self.site.save()
        resp = self.client.get("/")
        self.assertEqual(resp.context['secure_blocks_domain'], parent_site)

    def test_parent_domain_context_variable_visit_parent_site(self):
        child_site = factories.SeoSiteFactory()
        child_site.domain = "zz." + child_site.domain
        child_site.parent_site = self.site
        self.site.save()
        resp = self.client.get("/")
        self.assertEqual(resp.context['secure_blocks_domain'],
                         self.site)

    def test_parent_domain_context_variable_with_domain_switching(self):
        self.setup_superuser()
        parent_site = factories.SeoSiteFactory()
        child_site = factories.SeoSiteFactory()
        child_site.parent_site = parent_site
        child_site.domain="parentchildtest"
        child_site.save()
        resp = self.client.get("/?domain=parentchildtest")
        self.assertEqual(resp.context['secure_blocks_domain'], parent_site)
