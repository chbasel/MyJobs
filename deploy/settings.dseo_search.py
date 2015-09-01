import datetime
from S3 import CallingFormat

from default_settings import *
from dseo_celery import *
from secrets import REDIRECT_PROD, ARCHIVE_PROD, REDIRECT_QC


ALLOWED_HOSTS = ['*', ]

DATABASES = {
    'default': dict({
        'NAME': 'redirect',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'db-redirect.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }, **REDIRECT_PROD),
    'qc-redirect': dict({
        'NAME': 'redirect',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'db-redirectqc.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }, **REDIRECT_QC),
    'archive': dict({
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'redirect',
        'HOST': 'db-redirectarchive.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }, **ARCHIVE_PROD)
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'seo.search_backend.DESolrEngine',
        'URL': 'http://solr_server:8983/solr',
        'TIMEOUT': 60*3,
        'BATCH_SIZE': 1000
    },
    'groups': {
        'ENGINE': 'saved_search.groupsearch.SolrGrpEngine',
        'URL': 'http://solr_server:8983/solr'
    }
}

TEMPLATE_DIRS = (
    '/home/web/MyJobs/MyJobs/templates/',
)

SESSION_CACHE_ALIAS = 'sessions'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        # Set version number to date that project directory was last modified
        # This should update the cache key on deployments and ensure any servers
        # deployed to on the same day will have matching keys. Won't work for
        # multiple deployments per day.
        'VERSION': str(datetime.date.fromtimestamp(os.path.getmtime(__file__))),
        'LOCATION': [
            'dseo-mc-cluster.qksjst.0003.use1.cache.amazonaws.com:11211',
            'dseo-mc-cluster.qksjst.0004.use1.cache.amazonaws.com:11211',
        ]
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            'dseomj-mc-cluster.qksjst.0001.use1.cache.amazonaws.com:11211',
            'dseomj-mc-cluster.qksjst.0002.use1.cache.amazonaws.com:11211',
        ]
    },
}

AWS_STORAGE_BUCKET_NAME = 'src-nlx-org'
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

ROOT_URLCONF = 'dseo_urls'
MIDDLEWARE_CLASSES += (
    'wildcard.middleware.WildcardMiddleware',
    'middleware.RedirectOverrideMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS += (
    "social_links.context_processors.social_links_context",
    "seo.context_processors.site_config_context",
)

SOLR = {
    'all': 'http://ec2-23-20-67-65.compute-1.amazonaws.com:8983/solr/myjobs_test/',
    'current': 'http://ec2-23-20-67-65.compute-1.amazonaws.com:8983/solr/myjobs_test_current/',
    }

ABSOLUTE_URL = 'http://qc.secure.my.jobs/'

PROJECT = "dseo"
