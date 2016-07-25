import datetime

from default_settings import *
from dseo_celery import *
from secrets import REDIRECT_STAGING, ARCHIVE_STAGING, REDIRECT_QC


ALLOWED_HOSTS = ['*', ]

COMPRESS_ENABLED = True
COMPRESS_OFFLINE_MANIFEST = 'manifest.json'
STATIC_URL = "//d2e48ltfsb5exy.cloudfront.net/content_ms/files/"


DATABASES = {
    'default': dict({
        'NAME': 'redirect',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'db-redirectstaging.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }, **REDIRECT_STAGING),
    'qc-redirect': dict({
        'NAME': 'redirect',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'db-redirectqc.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }, **REDIRECT_QC),
    'archive': dict({
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'redirect',
        'HOST': 'db-redirectarchivestaging.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }, **ARCHIVE_STAGING)
}


SESSION_CACHE_ALIAS = 'sessions'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'VERSION': str(datetime.date.fromtimestamp(os.path.getmtime('.'))),
        'LOCATION': [
            'staging-mc-cluster.qksjst.0001.use1.cache.amazonaws.com:11211'
        ]
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            'staging-mc-cluster.qksjst.0001.use1.cache.amazonaws.com:11211'
        ]
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'seo.search_backend.DESolrEngine',
        'URL': 'http://ec2-54-225-127-98.compute-1.amazonaws.com:8983/solr',
        'TIMEOUT': 300,
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password']
    },
}

ROOT_URLCONF = 'dseo_urls'
MIDDLEWARE_CLASSES += (
    'wildcard.middleware.WildcardMiddleware',
    'middleware.RedirectOverrideMiddleware',
)
WILDCARD_REDIRECT=False
TEMPLATE_CONTEXT_PROCESSORS += (
    "social_links.context_processors.social_links_context",
    "seo.context_processors.site_config_context",
)

ABSOLUTE_URL = 'http://staging.secure.my.jobs/'

PROJECT = "dseo"


