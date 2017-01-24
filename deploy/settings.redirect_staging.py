from default_settings import *
from redirect_settings import *

from secrets import REDIRECT_STAGING, REDIRECT_QC, ARCHIVE_STAGING
import secrets

DEBUG = False
TEMPLATE_DEBUG = DEBUG

COMPRESS_ENABLED = True
COMPRESS_OFFLINE_MANIFEST = 'manifest.json'

STATIC_URL = "http://directemployers-staging.s3.amazonaws.com/Microsites/"

ABSOLUTE_URL = 'http://staging.secure.my.jobs/'

DATABASES = {
    'default': dict({
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'redirect',
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

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    'ec2-54-163-114-250.compute-1.amazonaws.com'
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SOLR = {
    'default': 'http://ec2-54-225-127-98.compute-1.amazonaws.com:8983/solr'
}

EMAIL_HOST_USER = STAGING_EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = STAGING_EMAIL_HOST_PASSWORD

setattr(secrets, 'MONGO_HOST', secrets.STAGING_MONGO_HOST)
setattr(secrets, 'MONGO_DBNAME', secrets.STAGING_MONGO_DBNAME)
setattr(secrets, 'MONGO_SSL', secrets.STAGING_MONGO_SSL)
