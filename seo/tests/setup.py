import os.path
from contextlib import contextmanager
from pymongoenv.tests import MongoTestMixin

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import clear_url_caches
from django.db import connections
from django.test import TransactionTestCase, override_settings
from django.test.client import Client
from django.template import context

from import_jobs.init import DATA_DIR
from saved_search.groupsearch import SolrGrpEngine, SolrGroupSearchBackend
from seo.search_backend import DESolrSearchBackend, DESolrEngine
from seo.tests.factories import BusinessUnitFactory, CompanyFactory
from seo.tests.factories import SeoSiteFactory, ConfigurationFactory
from seo_pysolr import Solr
import solr_settings


class TestDESolrSearchBackend(DESolrSearchBackend):
    def search(self, *args, **kwargs):
        counter = getattr(settings, 'SOLR_QUERY_COUNTER', 0)
        settings.SOLR_QUERY_COUNTER = counter + 1
        return super(TestDESolrSearchBackend, self).search(*args, **kwargs)


class TestDESolrEngine(DESolrEngine):
    backend = TestDESolrSearchBackend


class TestSolrGrpSearchBackend(SolrGroupSearchBackend):
    def search(self, *args, **kwargs):
        counter = getattr(settings, 'SOLR_QUERY_COUNTER', 0)
        settings.SOLR_QUERY_COUNTER = counter + 1
        return super(TestDESolrSearchBackend, self).search(*args, **kwargs)


class TestSolrGrpEngine(SolrGrpEngine):
    backend = TestSolrGrpSearchBackend


@override_settings(ROOT_URLCONF="dseo_urls", PROJECT="dseo", MEMOIZE=False,
                   HAYSTACK_CONNECTIONS=settings.TEST_HAYSTACK_CONNECTIONS,
                   MIDDLEWARE_CLASSES=settings.MIDDLEWARE_CLASSES,
                   TEMPLATES=settings.TEMPLATES)
class DirectSEOBase(MongoTestMixin, TransactionTestCase):

    fixtures = ['deploy/initial_data.json']

    def setUp(self):
        super(DirectSEOBase, self).setUp()

        db_backend = settings.DATABASES['default']['ENGINE'].split('.')[-1]

        # Set columns that are utf8 in production to utf8
        if db_backend == 'mysql':
            cursor = connections['default'].cursor()
            cursor.execute("alter table seo_customfacet convert to character "
                           "set utf8 collate utf8_unicode_ci")
            cursor.execute("alter table seo_seositefacet convert to character "
                           "set utf8 collate utf8_unicode_ci")
            cursor.execute("alter table seo_company convert to character set "
                           "utf8 collate utf8_unicode_ci")
            cursor.execute("alter table seo_queryredirect convert to character "
                           "set utf8 collate utf8_unicode_ci")
            cursor.execute("alter table taggit_tag convert to character set "
                           "utf8 collate utf8_unicode_ci")
            cursor.execute("alter table taggit_taggeditem convert to "
                           "character set "
                           "utf8 collate utf8_unicode_ci")
            cursor.execute("alter table seo_seositeredirect convert to "
                           "character set utf8 collate utf8_unicode_ci")
            cursor.execute("alter table django_redirect convert to "
                           "character set utf8 collate utf8_unicode_ci")
            # We have a data migration that does this, but we don't run
            # migrations during tests (Django 1.6.5
            cursor.execute("ALTER TABLE django_flatpage CONVERT TO "
                           "CHARACTER SET utf8 COLLATE utf8_general_ci")
            cursor.execute("ALTER TABLE seo_custompage CONVERT TO "
                           "CHARACTER SET utf8 COLLATE utf8_general_ci")

        clear_url_caches()

        self.base_middleware_classes = settings.MIDDLEWARE_CLASSES
        middleware_classes = self.base_middleware_classes + (
            'wildcard.middleware.WildcardMiddleware',
            'middleware.RedirectOverrideMiddleware')
        settings.MIDDLEWARE_CLASSES =  middleware_classes

        self.base_context_processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
        settings.TEMPLATES[0]['OPTIONS']['context_processors'] += [
            "social_links.context_processors.social_links_context",
            "seo.context_processors.site_config_context",
        ]
        context._standard_context_processors = None

        self.conn = Solr(settings.HAYSTACK_CONNECTIONS['default']['URL'])
        self.conn.delete(q="*:*")
        cache.clear()
        clear_url_caches()

        # As we added tests that created more and more companies, we
        # approached the hardcoded companies in import_jobs_testdata.json.
        # When we hit those ids, we began to get IntegrityErrors during
        # testing. Reset the sequence used by CompanyFactory to clear this
        # build-up.
        CompanyFactory.reset_sequence()

    def tearDown(self):
        super(DirectSEOBase, self).tearDown()

        settings.TEMPLATES[0]['OPTIONS']['context_processors'] = self.base_context_processors
        context._standard_context_processors = None
        setattr(settings, 'MIDDLEWARE_CLASSES',
                self.base_middleware_classes)


class DirectSEOTestCase(DirectSEOBase):
    def setUp(self):
        super(DirectSEOTestCase, self).setUp()
        self.solr_docs = solr_settings.SOLR_FIXTURE
        self.conn.add(self.solr_docs)

        # uids and numjobs in feed file for test business unit 0
        self.feed_uids = [57621597, 57311147, 60351047, 59891656, 58867671,
                          57495178, 59773973, 59326433, 57311143, 57311166]
        self.feed_numjobs = 14

        self.businessunit = BusinessUnitFactory(id=0)
        self.buid_id = self.businessunit.id
        # Ensure DATA_DIR used by import_jobs.download_feed_file exists
        data_path = DATA_DIR
        if not os.path.exists(data_path):
            os.mkdir(data_path)

    def tearDown(self):
        super(DirectSEOTestCase, self).tearDown()
        self.conn.delete(q="*:*")
        self.assertEqual(self.conn.search(q='*:*').hits, 0)


class DirectSeoTCWithSiteAndConfig(DirectSEOTestCase):
    """
        Test case with a job added and site configured
        Attributes:
            site - test seosite instance
            config - config for test seosite
            client - same as default client, but uses test seosite's domain as HTTP_HOST
    """
    def setUp(self):
        super(DirectSeoTCWithSiteAndConfig, self).setUp()
        self.site = SeoSiteFactory()
        self.site.business_units.add(self.businessunit)

        self.config = ConfigurationFactory.build(status=2)
        self.config.save()

        self.site.configurations.add(self.config)

        # ensure tests in this class use the correct domain
        self.client = Client(HTTP_HOST=self.site.domain)


class SettingDoesNotExist:
    pass


@contextmanager
def patch_settings(**kwargs):
    from django.conf import settings
    old_settings = []
    for key, new_value in kwargs.items():
        old_value = getattr(settings, key, SettingDoesNotExist)
        old_settings.append((key, old_value))
        setattr(settings, key, new_value)
    yield

    for key, old_value in old_settings:
        if old_value is SettingDoesNotExist:
            delattr(settings, key)
        else:
            setattr(settings, key, old_value)
