from datetime import date, timedelta, datetime
from itertools import chain, izip_longest
import logging
import pysolr
import urlparse

import boto
from celery import task
from celery.schedules import crontab

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.template.loader import render_to_string
from django.db.models import Q

from myjobs.models import EmailLog, User
from myprofile.models import SecondaryEmail
from mysearches.models import SavedSearch, SavedSearchDigest
from registration.models import ActivationProfile
from solr import signals as solr_signals
from solr.models import Update
from solr.signals import object_to_dict, profileunits_to_dict

logger = logging.getLogger(__name__)


@task(name='tasks.send_search_digest', ignore_result=True)
def send_search_digest(search):
    """
    Task used by send_send_search_digests to send individual digest or search
    emails.

    Inputs:
    :search: SavedSearch or SavedSearchDigest instance to be mailed
    """
    search.send_email()

@task(name='tasks.send_search_digests')
def send_search_digests():
    """
    Daily task to send saved searches. If user opted in for a digest, they
    receive it daily and do not get individual saved search emails. Otherwise,
    each active saved search is sent individually.
    """

    def filter_by_time(qs):
        """
        Filters the provided query set for emails that should be sent today

        Inputs:
        :qs: query set to be filtered

        Outputs:
        :qs: filtered query set containing today's outgoing emails
        """
        today = datetime.today()
        day_of_week = today.isoweekday()

        daily = qs.filter(frequency='D')
        weekly = qs.filter(frequency='W', day_of_week=str(day_of_week))
        monthly = qs.filter(frequency='M', day_of_month=today.day)
        return chain(daily, weekly, monthly)

    digests = SavedSearchDigest.objects.filter(is_active=True)
    digests = filter_by_time(digests)
    for obj in digests:
        send_search_digest.s(obj).apply_async()

    not_digest = SavedSearchDigest.objects.filter(is_active=False)
    for item in not_digest:
        saved_searches = item.user.savedsearch_set.filter(is_active=True)
        saved_searches = filter_by_time(saved_searches)
        for search_obj in saved_searches:
            send_search_digest.s(search_obj).apply_async()


@task(name='task.delete_inactive_activations')
def delete_inactive_activations():
    """
    Daily task checks if a activation keys are expired and deletes them.
    Disabled users are exempt from this check.
    """
    
    for profile in ActivationProfile.objects.all():
        try:
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_disabled and not user.is_active:
                    user.delete()
                    profile.delete()
        except User.DoesNotExist:
            profile.delete()


@task(name='tasks.process_batch_events')
def process_batch_events():
    """
    Processes all events that have accumulated over the last day, sends emails
    to inactive users, and disables users who have been inactive for a long
    period of time.
    """
    now = date.today()
    EmailLog.objects.filter(received__lte=now-timedelta(days=60),
                            processed=True).delete()
    new_logs = EmailLog.objects.filter(processed=False)
    for log in new_logs:
        user = User.objects.get_email_owner(email=log.email)
        if not user:
            # This can happen if a user removes a secondary address or deletes
            # their account between interacting with an email and the batch
            # process being run
            # There is no course of action but to ignore that event
            continue
        if user.last_response < log.received:
            user.last_response = log.received
            user.save()
        log.processed = True
        log.save()
    # These users have not responded in a month. Send them an email if they
    # own any saved searches
    inactive = User.objects.select_related('savedsearch_set')
    inactive = inactive.filter(Q(last_response=now-timedelta(days=30)) |
                               Q(last_response=now-timedelta(days=36)))

    for user in inactive:
        if user.savedsearch_set.exists():
            time = (now - user.last_response).days
            message = render_to_string('myjobs/email_inactive.html',
                                       {'user': user,
                                        'time': time})
            user.email_user('Account Inactivity', message,
                            settings.DEFAULT_FROM_EMAIL)

    # These users have not responded in a month and a week. Stop sending emails.
    stop_sending = User.objects.filter(
        last_response__lte=now-timedelta(days=37))
    for user in stop_sending:
        user.opt_in_myjobs = False
        user.save()

@task(name="tasks.update_solr")
def update_solr_task(solr_location=settings.SOLR['default']):
    """
    Deletes all items scheduled for deletion, and then adds all items
    scheduled to be added to solr.

    """

    if hasattr(mail, 'outbox'):
        solr_location = 'http://127.0.0.1:8983/solr/myjobs_test/'
    objs = Update.objects.filter(delete=True).values_list('uid', flat=True)

    if objs:
        objs = split_list(objs, 1000)
        for obj_list in objs:
            obj_list = filter(None, list(obj_list))
            uid_list = " OR ".join(obj_list)
            solr = pysolr.Solr(solr_location)
            solr.delete(q="uid:(%s)" % uid_list)
            Update.objects.filter(delete=True).delete()

    objs = Update.objects.filter(delete=False)
    solr = pysolr.Solr(solr_location)
    updates = []

    for obj in objs:
        content_type, key = obj.uid.split("##")
        model = ContentType.objects.get(pk=content_type).model_class()
        if model == SavedSearch:
            updates.append(object_to_dict(model, model.objects.get(pk=key)))
        # If the user is being updated, because the user is stored on the
        # SavedSearch document, every SavedSearch belonging to that user
        # also has to be updated.
        elif model == User:
            searches = SavedSearch.objects.filter(user_id=key)
            [updates.append(object_to_dict(SavedSearch, s)) for s in searches]
            updates.append(object_to_dict(model, model.objects.get(pk=key)))
        else:
            updates.append(profileunits_to_dict(key))

    updates = split_list(updates, 1000)
    for update_subset in updates:
        update_subset = filter(None, list(update_subset))
        solr.add(list(update_subset))
    objs.delete()


def split_list(l, list_len, fill_val=None):
    """
    Splits a list into sublists.

    inputs:
    :l: The list to be split.
    :list_len: The length of the resulting lists.
    :fill_val: The value that is inserted when there are less items in the
        final list than list_len.

    outputs:
    A generator of tuples size list_len.

    """
    args = [iter(l)] * list_len
    return izip_longest(fillvalue=fill_val, *args)


@task(name="tasks.reindex_solr")
def task_reindex_solr(solr_location=settings.SOLR['default']):
    """
    Adds all ProfileUnits, Users, and SavedSearches to solr.

    """
    solr = pysolr.Solr(solr_location)
    l = []

    u = User.objects.all().values_list('id', flat=True)
    for x in u:
        l.append(profileunits_to_dict(x))

    s = SavedSearch.objects.all()
    for x in s:
        l.append(object_to_dict(SavedSearch, x))

    u = User.objects.all()
    for x in u:
        l.append(object_to_dict(User, x))

    l = split_list(l, 1000)
    for x in l:
        x = filter(None, list(x))
        solr.add(x)


@task(name="tasks.read_new_logs")
def read_new_logs():
    """
    Reads new logs and stores their contents in solr
    """
    def parse_log(key):
        update = []
        contents = key.get_contents_as_string().splitlines()
        for line in contents:
            line = line.split()
            content_dict = {'datetime': line[0],
                            'aguid': line[7],
                            'myguid': line[8],
                            'url': line[9]}
            qs = urlparse.parse_qs(line[4])
            content_dict['url'] = qs.get('url', '')
            update.append(content_dict)
        return update

    conn = boto.connect_s3(aws_access_key_id=settings.S3_ACCESS_KEY,
                           aws_secret_access_key=settings.S3_SECRET_KEY)
    # https://github.com/boto/boto/issues/2078
    # validate=True costs 13.5x validate=False; Skip validation if we are
    # reasonably certain that the bucket exists.
    log_bucket = conn.get_bucket('my-jobs-logs', validate=False)
    keys = log_bucket.list()
    to_solr = []
    for key in keys:
        to_solr += parse_log(key)
