import datetime

from default_settings import *
from secrets import REDIRECT_QC, ARCHIVE_STAGING, REDIRECT_STAGING
import secrets

COMPRESS_ENABLED = True
COMPRESS_OFFLINE_MANIFEST = 'manifest.json'

ALLOWED_HOSTS = ['*', ]


DATABASES = {
    'default': dict({
        'NAME': 'redirect',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'db-redirectqc.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }, **REDIRECT_QC),
    # Points to staging instead of QC for testing purposes.
    'qc-redirect': dict({
        'NAME': 'redirect',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'db-redirectstaging.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }, **REDIRECT_STAGING),
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
        'URL': 'http://ec2-52-7-65-86.compute-1.amazonaws.com:8983/solr/qc',
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

ABSOLUTE_URL = 'http://qc.secure.my.jobs/'

PROJECT = "dseo"


BROKER_HOST = '204.236.236.123'
BROKER_PORT = 5672
BROKER_USER = 'celery'
BROKER_VHOST = 'dseo-qc'

CELERY_DEFAULT_EXCHANGE = 'tasks'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_DEFAULT_ROUTING_KEY = 'dseo.default'
CELERY_QUEUES = {
    'dseo': {
        'binding_key': 'dseo.#'
    },
    'solr': {
        'binding_key': 'solr.#'
    }
}
CELERY_ROUTES = {
    'tasks.task_update_solr': {
        'queue': 'solr',
        'routing_key': 'solr.update_solr'
    },
    'tasks.task_clear_solr': {
        'queue': 'solr',
        'routing_key': 'solr.clear_solr'
    },
    'tasks.etl_to_solr': {
        'queue': 'solr',
        'routing_key': 'solr.update_solr'
    },
}

setattr(secrets, 'MONGO_HOST', secrets.QC_MONGO_HOST)
setattr(secrets, 'MONGO_DBNAME', secrets.QC_MONGO_DBNAME)
setattr(secrets, 'MONGO_SSL', secrets.QC_MONGO_SSL)

from pymongoenv import change_db
change_db(secrets.QC_MONGO_HOST, secrets.QC_MONGO_DBNAME, secrets.QC_MONGO_SSL)
