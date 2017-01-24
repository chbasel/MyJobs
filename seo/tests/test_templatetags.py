# -*- coding: utf-8 -*-
from collections import namedtuple
from urllib import quote_plus

from django.test.client import RequestFactory

from seo.templatetags.seo_extras import joblist_url
from setup import DirectSEOBase


Job = namedtuple('Job', 'location title guid')


class JobListURLTest(DirectSEOBase):
    @staticmethod
    def get_request(querystring=None):
        """
        :param querystring:
        :return: A fake request.

        """
        url = '/jobs/' if not querystring else '/jobs/?%s' % querystring
        return RequestFactory().get(url)

    @staticmethod
    def get_job(location='Avon, IN', title='Software', guid='A'*32):
        """
        Generate a fake "job" with location, title, and guid attributes which
        are required by the joblist_url function.

        :param location: The location of the fake job.
        :param title: The title of the fake job.
        :param guid: A fake guid for the fake job.

        :return: A namedtuple with all attributes required for a job in
                 joblist_url set.

        """
        return Job(location=location, title=title, guid=guid)

    def test_unicode(self):
        """
        Unicode characters in the persistent querystring parameters
        should not prevent the url from being generated.

        """
        unicode_title = u'Розничная'
        encoded_unicode_title = quote_plus(unicode_title.encode('utf8'))
        utm_campaign = u'utm_campaign=%s' % unicode_title
        encoded_utm_campaign = u'utm_campaign=%s' % encoded_unicode_title
        context = {'request': self.get_request(querystring=utm_campaign)}
        job = self.get_job()

        url = joblist_url(context, job)
        self.assertIn(job.guid, url)
        self.assertIn(encoded_utm_campaign, url)

    def test_persisting_params(self):
        """
        The querystring parameters that were requested to persist
        to the apply page should in fact be persistent.

        """
        params_to_persist = [
            'de_n', 'de_m', 'de_t', 'de_o', 'de_c', 'utm_source', 'utm_medium',
            'utm_term', 'utm_content', 'utm_campaign'
        ]

        for param in params_to_persist:
            querystring = '%s=VALUE_FOR_PARAM%s' % (param, param)
            context = {'request': self.get_request(querystring)}
            job = self.get_job()

            url = joblist_url(context, job)
            self.assertIn(querystring, url)

    def test_apply_param_from_cookie(self):
        """
        If the value for a parameter we persist is stored in a cookie but not
        the url, the value from the cookie should still end up on the url
        returned by joblist_url.

        """
        cookie_field_mappings = {
            'external_utm_campaign': 'utm_campaign',
            'external_utm_medium': 'utm_medium',
            'external_utm_content': 'utm_content',
            'external_utm_source': 'utm_source',
            'external_utm_term': 'utm_term',
        }
        for cookie_name, param_name in cookie_field_mappings.iteritems():
            cookie_val = 'COOKIE_%s' % param_name
            querystring = "%s=%s" % (param_name, cookie_val)

            request = self.get_request()
            request.COOKIES[cookie_name] = cookie_val
            context = {'request': request}
            job = self.get_job()

            url = joblist_url(context, job)

            self.assertIn(querystring, url)

    def test_url_over_cookie(self):
        """
        A parameter value retrieved via url should always be preferred over
        one retrieved via cookie.

        """
        cookie_field_mappings = {
            'external_utm_campaign': 'utm_campaign',
            'external_utm_medium': 'utm_medium',
            'external_utm_content': 'utm_content',
            'external_utm_source': 'utm_source',
            'external_utm_term': 'utm_term',
        }
        for cookie_name, param_name in cookie_field_mappings.iteritems():
            cookie_val = 'COOKIE_%s' % param_name
            querystring_val = 'QUERYSTRING_%s' % param_name
            querystring = "%s=%s" % (param_name, querystring_val)

            request = self.get_request(querystring=querystring)
            request.COOKIES[cookie_name] = cookie_val
            context = {'request': request}
            job = self.get_job()

            url = joblist_url(context, job)

            self.assertIn(querystring, url)
            self.assertNotIn(cookie_val, url)
