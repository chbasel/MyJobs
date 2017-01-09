from S3 import CallingFormat
from default_settings import *
import datetime
import os

from secrets import REDIRECT_QC, ARCHIVE_STAGING, REDIRECT_STAGING
import secrets

DEBUG = True

COMPRESS_ENABLED = True
COMPRESS_OFFLINE_MANIFEST = 'manifest.json'

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

ALLOWED_HOSTS = ['my.jobs', 'localhost']

_PATH = os.path.abspath(os.path.dirname(__file__))


# Absolute URL used for cross site links, relative during local/staging
# absolute during production
ABSOLUTE_URL = 'http://qc.secure.my.jobs/'

PROJECT = "myjobs"
ENVIRONMENT = 'QC'

SESSION_CACHE_ALIAS = 'sessions'
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
    },
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

AWS_STORAGE_BUCKET_NAME = 'my-jobs'
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

CC_AUTH = TESTING_CC_AUTH

ROOT_URLCONF = 'myjobs_urls'


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'seo.search_backend.DESolrEngine',
        # 'solr_server' must be defined in /etc/hosts on the server where this
        # code is deployed. Check the deployment project in
        # direct_seo/web/conf/hosts and make sure the one in production looks
        # like that.
        'URL': 'http://solr_server:8983/solr/qc',
        'TIMEOUT': 300,
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password']
    },
    'groups': {
        'ENGINE': 'saved_search.groupsearch.SolrGrpEngine',
        'URL': 'http://solr_server:8983/solr/qc',
        'TIMEOUT': 300,
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password']
    }
}

TEMPLATE_CONTEXT_PROCESSORS += (
    'mymessages.context_processors.message_lists',
)

EMAIL_HOST_USER = QC_EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = QC_EMAIL_HOST_PASSWORD

CELERY_ALWAYS_EAGER = True

LOGGING['loggers']['mypartners.views']['level'] = 'INFO'

# The email host used to parse communication records
PRM_EMAIL_HOST = 'qc.my.jobs'

setattr(secrets, 'MONGO_HOST', secrets.QC_MONGO_HOST)
setattr(secrets, 'MONGO_DBNAME', secrets.QC_MONGO_DBNAME)
setattr(secrets, 'MONGO_SSL', secrets.QC_MONGO_SSL)
