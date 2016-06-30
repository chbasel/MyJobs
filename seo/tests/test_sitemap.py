# -*- coding: utf-8 -*-
import datetime

from django.conf import settings

from seo.models import SeoSite
from seo.tests.solr_settings import SOLR_FIXTURE
from setup import DirectSEOBase


class SitemapTestCase(DirectSEOBase):
    def setUp(self):
        super(SitemapTestCase, self).setUp()

    def tearDown(self):
        super(SitemapTestCase, self).tearDown()
        self.conn.delete("*:*")

    def test_index(self):
        resp = self.client.get("/sitemap.xml")
        self.assertEqual(resp.status_code, 200)

    def test_no_buid_sitemap(self):
        """
        Test to verify that a sitemap is generated with sites that have no
        BUID.

        """
        site = SeoSite.objects.get(id=1)
        site.business_units = []
        site.save()
        job = dict(SOLR_FIXTURE[0])
        self.conn.add([job])
        resp = self.client.get("/sitemap-0.xml")
        self.assertTrue("<url>" in resp.content)

    def test_noreverse(self):
        """
        Test to ensure that jobs with bad/ugly data do not block the
        creation of a sitemap page, but instead are just skipped over in
        `SolrSitemap.get_urls().`

        This is a regression test. It was prompted by a job in a job feed
        file having "~" in the "city" field. Because our URL pattern
        doesn't recognize that character in its regex, it caused a
        `NoReverseMatch` exception to be thrown. Instead of adding a
        tilde, we want to be able to handle any weird characters not
        specified in our URL config.

        """
        # Sometimes the site settings are messed up from other tests. Ensure
        # that the settings are compatible with actually searching for the
        # jobs we're adding.
        settings.SITE_BUIDS = []
        site = SeoSite.objects.get(pk=1)
        site.business_units = []
        site.save()

        # These are kwargs from the actual error that created this error in the
        # first place.
        kwargs = {
            'location': '~, WV',
            'title': '911 Coordinator',
            'uid': '25901630'
        }
        job = dict(SOLR_FIXTURE[0])
        job.update(kwargs)
        self.conn.add([job])
        resp = self.client.get("/sitemap-0.xml")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue("<url>" in resp.content)
