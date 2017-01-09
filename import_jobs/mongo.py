from pymongoenv import connect_db
import re
from seo.helpers import create_businessunit
from seo.models import BusinessUnit
from import_jobs.init import add_company, get_jobsfs_zipfile, get_jobs_from_zipfile,\
    filter_current_jobs, DATA_DIR, download_feed_file, FeedImportError
from transform import hr_xml_to_json

import logging
from xmlparse import DEv2JobFeed
logger = logging.getLogger(__name__)


def jobsfs_to_mongo(guid, buid, name):
    """Composed method for resopnding to a guid update."""

    assert re.match(r'^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$', guid.upper()), \
           "%s is not a valid guid" % guid
    assert re.match(r'^\d+$', str(buid)), "%s is not a valid buid" % buid

    logger.info("Updating Job Source %s", guid)
    # Make the BusinessUnit and Company
    create_businessunit(buid)
    bu = BusinessUnit.objects.get(id=buid)
    bu.title = name
    bu.save()
    add_company(bu)

    # Lookup the jobs, filter then, transform them, and then load the jobs
    zf = get_jobsfs_zipfile(guid)
    jobs = get_jobs_from_zipfile(zf, guid)
    jobs = filter_current_jobs(jobs, bu)
    jobs = (hr_xml_to_json(job, bu) for job in jobs)
    jobs = list(jobs)
    for job in jobs:
        job['guid'] = job['guid'].lower()

    if len(jobs) > 0:
        collection = connect_db().db.jobs
        bulk = collection.initialize_unordered_bulk_op()
        for job in jobs:
            bulk.find({'guid': job['guid']}).upsert().replace_one(job)
        bulk.execute()


def seoxml_to_mongo(buid, data_dir=DATA_DIR):
    filepath = download_feed_file(buid, data_dir=data_dir)

    jobfeed = DEv2JobFeed(filepath, jsid=buid, markdown=False,
                          company=None)
    # If the feed file did not pass validation, return. The return value is
    # '(0, 0)' to match what's returned on a successful parse.
    if jobfeed.errors:
        error = jobfeed.error_messages
        logging.error("BUID:%s - Feed file has failed validation on line %s. "
                      "Exception: %s" % (buid, error['line'],
                                         error['exception']))
        raise FeedImportError(error)

    # A dictionary of uids
    jobfeed.jobparse()
    jobs = jobfeed.solr_jobs()

    collection = connect_db().db.jobs
    bulk = collection.initialize_unordered_bulk_op()
    for job in jobs:
        job['guid'] = job['guid'].lower()
        bulk.find({'guid': job['guid']}).upsert().replace_one(job)
    bulk.execute()
