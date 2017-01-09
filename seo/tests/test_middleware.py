import datetime

from django.conf import settings

from seo.tests.factories import (SeoSiteFactory, SeoSiteRedirectFactory)
from seo.models import BusinessUnit, SeoSite, QueryRedirect, QParameter, \
    LocationParameter
from setup import DirectSEOBase
import thread_manager


class SiteRedirectMiddlewareTestCase(DirectSEOBase):
    def setUp(self):
        super(SiteRedirectMiddlewareTestCase, self).setUp()
        self.test_site = SeoSiteFactory.build()
        self.test_site.save()
        self.ssr1 = SeoSiteRedirectFactory.build(seosite=self.test_site)
        self.ssr1.save()
        self.ssr2 = SeoSiteRedirectFactory.build(
                    redirect_url=u'test.%s' % self.test_site.domain,
                    seosite=self.test_site)
        self.ssr2.save()

    def test_host_is_a_redirect(self):
        """
        This tests that the passed in HOST needs to be redirected to
        another URL. The path that we go to is used to test that the
        path is consistent across redirects.

        """
        response = self.client.get(
            '/style/style.css',
            HTTP_HOST=u'.'.join([u'www', self.test_site.domain]),
            follow=True)
        redirect_url, status_code = response.redirect_chain[0]
        self.assertEqual(status_code, 301)
        self.assertEqual(redirect_url,
                         u'http://%s/style/style.css' % self.test_site.domain)

    def test_host_is_not_a_redirect(self):
        """
        This tests that the passed in HOST is the default domain name.

        """
        response = self.client.get('/style/style.css',
                                   HTTP_HOST=self.test_site.domain,
                                   follow=True)
        status_code = response.status_code
        redirect_chain = response.redirect_chain
        self.assertNotEqual(status_code, 301)
        # test here that there were no redirects, the chain should be empty
        self.assertEqual(len(redirect_chain), 0)

    def test_host_doesnt_exist(self):
        """
        Given our system, this one is a little tough to test, the URL
        is obviously not in the test database (not created in setup), so
        as long as it doesn't redirect, then I think this test passes.
        Yes...this is a little loose.

        """
        response = self.client.get('/', HTTP_HOST=u'buckconsultants.jobs',
                                   follow=True)
        redirect_chain = response.redirect_chain
        self.assertEqual(len(redirect_chain), 0)


class MultiHostMiddlewareTestCase(DirectSEOBase):
    def setUp(self):
        super(MultiHostMiddlewareTestCase, self).setUp()
        self.bu = BusinessUnit(id=42, date_crawled=datetime.datetime.now(),
                               date_updated=datetime.datetime.now())
        self.test_site = SeoSiteFactory(
            domain=u'buckconsultants.jobs',
            name=u'buckconsultants')

    def test_existant_site(self):
        # test the site_id, site name, buids, etc
        self.client.get('/', HTTP_HOST=self.test_site.domain)
        self.assertEqual(thread_manager.get('SITE_ID'), self.test_site.id)
        self.assertEqual(settings.SITE_NAME, self.test_site.name)

    def test_non_existant_site(self):
        # 1 is the deafult site that we end up getting in middleware,
        # so use that to compare the results to.
        site = SeoSite.objects.get(pk=1)

        # test that the site returned is the default site
        response = self.client.get('/', HTTP_HOST='jklsdasdfj.jobs')
        self.assertEqual(thread_manager.get('SITE_ID'), 1)
        self.assertEqual(settings.SITE_NAME, site.name)
        self.assertEqual(len(settings.SITE_BUIDS), site.business_units.all().count())


class RedirectOverrideMiddlewareTestCase(DirectSEOBase):
    def setUp(self):
        super(RedirectOverrideMiddlewareTestCase, self).setUp()
        self.site = SeoSite.objects.get()
        self.other_site = SeoSiteFactory(domain=u'buckconsultants.jobs',
                                         name=u'buckconsultants')

        self.redirect = QueryRedirect.objects.create(
            site=self.site, old_path='/jobs/',
            new_path='https://www.google.com')

    def test_query_redirect_without_queries(self):
        """
        Requests for a given site/path should redirect on that site if the
        request doesn't contain query parameters and should not occur for
        other sites.
        """
        response = self.client.get(self.redirect.old_path + '?q=foo',
                                   HTTP_HOST=self.site.domain)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.redirect.old_path,
                                   HTTP_HOST=self.site.domain)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], self.redirect.new_path)

        response = self.client.get(self.redirect.old_path,
                                   HTTP_HOST=self.other_site.domain)
        self.assertEqual(response.status_code, 200)

    def test_query_redirect_with_queries(self):
        """
        Requests for a given site/path and a number of query strings should
        redirect only on that site, only if all query strings are present, and
        only if the request doesn't contain additional query parameters that
        we look for.
        """
        q = QParameter.objects.create(redirect=self.redirect, value="sales")
        location = LocationParameter.objects.create(redirect=self.redirect,
                                                    value="Indianapolis")

        response = self.client.get(
            self.redirect.old_path + '?moc=foo&location=' + location.value +
            '&q=' + q.value,
            HTTP_HOST=self.site.domain
        )
        self.assertEqual(response.status_code, 200,
                         "Query redirect took place with too many parameters")

        # q.value.upper() is not required but it also shows that this check
        # is case-insensitive.
        response = self.client.get(
            self.redirect.old_path + '?location=' + location.value + '&q='
            + q.value.upper(),
            HTTP_HOST=self.site.domain
        )
        self.assertEqual(response.status_code, 301,
                         "Query redirect did not take place")
        self.assertEqual(response['Location'], self.redirect.new_path)

        response = self.client.get(
            self.redirect.old_path + '?location=' + location.value,
            HTTP_HOST=self.site.domain
        )
        self.assertEqual(response.status_code, 200,
                         "Query redirect took place despite a missing query")

        response = self.client.get(
            self.redirect.old_path + '?location=' + location.value + '&q='
            + q.value.upper(),
            HTTP_HOST=self.other_site.domain
        )
        self.assertEqual(response.status_code, 200,
                         "Query redirect took place on the wrong site")
