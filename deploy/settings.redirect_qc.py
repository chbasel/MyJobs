from default_settings import *
from redirect_settings import *

from secrets import (REDIRECT_STAGING, REDIRECT_QC, ARCHIVE_STAGING,
                     STAGING_MONGO_HOST, STAGING_MONGO_SSL,
                     STAGING_MONGO_DBNAME)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

COMPRESS_ENABLED = True
COMPRESS_OFFLINE_MANIFEST = 'manifest.json'

STATIC_URL = "http://directemployers-staging.s3.amazonaws.com/Microsites/"

ABSOLUTE_URL = 'http://qc.secure.my.jobs/'

DATABASES = {
    'default': dict({
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'redirect',
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

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    'ec2-34-195-101-13.compute-1.amazonaws.com',
    'qc.my.jobs',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SOLR = {
    'default': 'http://ec2-54-225-127-98.compute-1.amazonaws.com:8983/solr'
}

EMAIL_HOST_USER = QC_EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = QC_EMAIL_HOST_PASSWORD

setattr(secrets, 'MONGO_HOST', secrets.QC_MONGO_HOST)
setattr(secrets, 'MONGO_DBNAME', secrets.QC_MONGO_DBNAME)
setattr(secrets, 'MONGO_SSL', secrets.QC_MONGO_SSL)

from pymongoenv import change_db
change_db(secrets.QC_MONGO_HOST, secrets.QC_MONGO_DBNAME, secrets.QC_MONGO_SSL)
