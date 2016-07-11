from email.utils import getaddresses
from datetime import datetime
import json
from urllib import unquote
from urlparse import urlparse
import uuid

from django.conf import settings
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.http import (HttpResponseGone, HttpResponsePermanentRedirect,
                         HttpResponse, HttpResponseServerError,
                         HttpResponseNotFound)
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.utils import text, timezone
from django.views.decorators.csrf import csrf_exempt

from mypartners.models import OutreachEmailAddress
from redirect.helpers import get_job_from_solr

from redirect.models import (Redirect, CanonicalMicrosite,
                             DestinationManipulation, CompanyEmail,
                             EmailRedirectLog)
from redirect import helpers


def home(request, guid, vsid=None, debug=None):
    now = datetime.now(tz=timezone.utc)
    if vsid is None:
        vsid = '0'
    guid = '{%s}' % uuid.UUID(guid)

    # Providing z=1 as a query parameter enables custom parameters
    enable_custom_queries = request.REQUEST.get('z') == '1'
    expired = False
    user_agent_vs = None
    redirect_url = None

    if debug:
        # On localhost ip will always be empty unless you've got a setup
        # that mirrors production
        debug_content = ['ip=%s' % request.META.get('HTTP_X_FORWARDED_FOR', ''),
                         'GUID=%s' % guid]
        if enable_custom_queries:
            debug_content.append('CustomParameters=%s' %
                                 request.META.get('QUERY_STRING'))

    guid_redirect = helpers.get_redirect_or_404(guid=guid)
    cleaned_guid = helpers.clean_guid(guid_redirect.guid).upper()

    analytics = {
        'gu': cleaned_guid, 've': '1.0', 'vs': vsid, 'ia': 'uk', 'ev': 'rd',
        'cp': 'uk', 'tm': 'r', 'mo': '0',
        'ua': request.META.get('HTTP_USER_AGENT', '')
    }

    syndication_params = {'request': request, 'redirect': guid_redirect,
                          'guid': cleaned_guid, 'view_source': vsid}

    original_url = guid_redirect.url

    if debug:
        debug_content.append('RetLink(original)=%s' % guid_redirect.url)
        syndication_params['debug_content'] = debug_content

    response = helpers.get_syndication_redirect(**syndication_params)

    if response is None:
        user_agent_vs, response = helpers.get_opengraph_redirect(
            request, guid_redirect, cleaned_guid)

    if response is None:
        if vsid == '1604':
            # msccn redirect

            company_name = guid_redirect.company_name
            company_name = helpers.quote_string(company_name)
            redirect_url = ('http://us.jobs/msccn-referral.asp?gi='
                            '%s%s&cp=%s' %
                            (cleaned_guid,
                             vsid,
                             company_name))
        else:
            args = {'request': request, 'guid_redirect': guid_redirect,
                    'vsid': vsid, 'guid': cleaned_guid}
            if debug:
                args['debug_content'] = debug_content
            returned_dict = helpers.get_redirect_url(**args)
            redirect_url = returned_dict.get('redirect_url', '')
            facebook = returned_dict.get('facebook', False)
            expired = returned_dict.get('expired', False)
            browse_url = returned_dict.get('browse_url', '')
        if not redirect_url:
            redirect_url = guid_redirect.url
            params = {'request': request, 'url': redirect_url,
                      'exclude': True}
            if debug:
                debug_content.append(
                    'ManipulatedLink(No Manipulation)=%s' % redirect_url)
                params['debug_content'] = debug_content
            if enable_custom_queries:
                redirect_url = helpers.add_custom_queries(**params)
        redirect_url = helpers.get_hosted_state_url(guid_redirect,
                                                    redirect_url)

        if debug:
            debug_content.append('RetLink=%s' % redirect_url)

        if expired:
            err = '&jcnlx.err=XIN'
            data = {'job': guid_redirect,
                    'expired_url': original_url,
                    'view_source': vsid}
            if (guid_redirect.buid in [1228, 5480] or
                    2650 <= guid_redirect.buid <= 2703):
                if guid_redirect.buid in [1228, 5480]:
                    err = '&jcnlx.err=XJC'
                else:
                    err = '&jcnlx.err=XST'

            if browse_url:
                data['browse_url'] = browse_url
            else:
                data['browse_url'] = 'http://www.my.jobs/%s/careers/' % \
                    text.slugify(guid_redirect.company_name)
            response = HttpResponseGone(
                render_to_string('redirect/expired.html', data))
        else:
            response = HttpResponsePermanentRedirect(redirect_url)

        aguid = request.COOKIES.get('aguid') or \
            uuid.uuid4().hex
        if '%' in aguid:
            aguid = uuid.UUID(unquote(aguid)).hex
        myguid = request.COOKIES.get('myguid', '')
        analytics.update({'aguid': aguid, 'myguid': myguid})
        buid = helpers.get_Post_a_Job_buid(guid_redirect)
        qs = 'jcnlx.ref=%s&jcnlx.url=%s&jcnlx.buid=%s&jcnlx.vsid=%s&jcnlx.aguid=%s&jcnlx.myguid=%s'
        qs %= (helpers.quote_string(request.META.get('HTTP_REFERER', '')),
               helpers.quote_string(redirect_url),
               buid,
               vsid,
               aguid,
               myguid)
        if expired:
            d_seconds = (now - guid_redirect.expired_date).total_seconds()
            d_hours = int(d_seconds / 60 / 60)
            qs += '%s&jcnlx.xhr=%s' % (err, d_hours)

        response['X-REDIRECT'] = qs

        response = helpers.set_aguid_cookie(response,
                                            request.get_host(),
                                            aguid)

    if redirect_url and not expired:
        # If redirect_url has a value and expired does not, we're probably
        # going to redirect somewhere useful.
        parsed = urlparse(redirect_url)
        pn = parsed.path
        pr = parsed.scheme + ':'
        hn = parsed.netloc
        se = parsed.query
        if se:
            se = '?' + se
    else:
        # If redirect_url is blank or expired has a value, we're staying on the
        # my.jobs domain. We may show a "job expired" page, Open Graph info, or
        # something else.
        hn = request.get_host()
        pr = request.is_secure() and 'https:' or 'http:'
        pn = request.path
        se = request.META.get('QUERY_STRING', '')
        if se:
            se = '?' + se
    analytics.update({
        # Python doesn't have a method of easily creating a timestamp with
        # Zulu at the end. Replace one ISO-8601 supported format (+00:00)
        # with another (Z).
        'to': now.isoformat()[:-6] + 'Z', 'referrer': request.META.get('HTTP_REFERER', ''),
        'pn': pn, 'pr': pr, 'hn': hn, 'se': se})

    if debug and not user_agent_vs:
        data = {'debug_content': debug_content}
        response = render_to_response('redirect/debug.html',
                                      data,
                                      context_instance=RequestContext(request))

    return response


def myjobs_redirect(request):
    return HttpResponsePermanentRedirect(
        'http://www.my.jobs' + request.get_full_path())


@csrf_exempt
def email_redirect(request):
    """
    Accepts a post from SendGrid's mail parsing webhook and processes it.

    Authentication issues return a status code of 403
    All other paths return a 200 to prevent SendGrid from sending the same
        email repeatedly
    """
    if not helpers.is_authorized(request):
        return HttpResponse(status=403)

    try:
        to_email = request.POST.get('to', None)
        if to_email and type(to_email) != list:
            to_email = [to_email]
        elif not to_email:
            to_email = []
        body = request.POST.get('text', '')
        html_body = request.POST.get('html', '')
        from_email = request.POST.get('from', '')
        cc = request.POST.get('cc', None)
        if cc and type(cc) != list:
            cc = [cc]
        elif not cc:
            cc = []
        subject = request.POST.get('subject', '')
        num_attachments = int(request.POST['attachments'])
    except (KeyError, ValueError):
        # KeyError: key was not in POST dict
        # ValueError: num_attachments could not be cast
        #     to int
        return HttpResponse(status=200)

    attachment_data = []
    for file_number in range(1, num_attachments+1):
        try:
            file_ = request.FILES['attachment%s' % file_number]
        except KeyError:
            # Upload problem?
            helpers.log_failure(request.POST.copy(),
                                'My.jobs Attachment Failure')
            return HttpResponse(status=200)
        name = file_.name
        content = file_.read()
        content_type = file_.content_type
        attachment_data.append((name, content, content_type))

    addresses = getaddresses(to_email)
    addresses = [addr[1].lower() for addr in addresses]

    prm_bcc = False
    try:
        # prm@my.jobs appears in the 'envelope' parameter
        # posted from SendGrid if prm@my.jobs was added
        # via BCC
        envelope = json.loads(request.POST.get('envelope',
                                               ''))
    except ValueError:
        # envelope was not valid JSON or was not provided
        pass
    else:
        bcc_addresses = envelope.get('to', [])
        bcc_local = set(address.rsplit('@', 1)[0] for address in bcc_addresses)
        bcc_outreach = OutreachEmailAddress.objects.filter(email__in=bcc_local)
        if 'prm@my.jobs' in [env_email.lower()
                             for env_email
                             in bcc_addresses] or bcc_outreach.exists():
            prm_bcc = True

    local = set(address.rsplit('@', 1)[0] for address in addresses)
    outreach = OutreachEmailAddress.objects.filter(email__in=local)
    if prm_bcc or 'prm@my.jobs' in addresses or outreach.exists():
        # post to my.jobs
        helpers.repost_to_mj(request.POST.copy(),
                             attachment_data)
        if hasattr(mail, 'outbox'):
            return HttpResponse(content='reposted')
        return HttpResponse(status=200)
    if len(addresses) != 1:
        # >1 recipients in the "to" field or everyone is (b)cc
        # Probably not a guid@my.jobs email
        return HttpResponse(status=200)
    hex_guid = addresses[0].split('@')[0]

    # shouldn't happen, but if someone somehow sends an
    # email with a view source attached, we should
    # remove it
    hex_guid = hex_guid[:32]

    email_dict = {'new_to': from_email,
                  'old_to': to_email,
                  'guid': hex_guid}

    try:
        to_guid = '{%s}' % uuid.UUID(hex_guid)
        job = Redirect.objects.get_any(guid=to_guid)
    except ValueError:
        # Not a guid
        return HttpResponse(status=200)
    except ObjectDoesNotExist:
        email_dict['email_type'] = 'no_job'
        helpers.send_response_to_sender(**email_dict)
        return HttpResponse(status=200)

    solr_job = get_job_from_solr(hex_guid)
    email_dict['solr_job'] = solr_job
    email_dict['job'] = job

    try:
        ce = CompanyEmail.objects.get(buid=job.buid)
        new_to = ce.email
    except CompanyEmail.DoesNotExist:
        email_dict['email_type'] = 'no_contact'
        helpers.send_response_to_sender(**email_dict)
        return HttpResponse(status=200)

    email_dict['email_type'] = 'contact'
    helpers.send_response_to_sender(**email_dict)

    sg_headers = {
        'X-SMTPAPI': '{"category": "My.jobs email redirect"}'
    }

    reqid = solr_job.get('reqid', 'None') if solr_job else 'Expired'
    subject = u'[ReqID: {reqid}] - {subject}'.format(
        reqid=reqid, subject=subject)

    # We want to ensure both text and html emails get sent, hence what could
    # be considered a bit of duplication.
    dashes = "----------------------"
    description = (solr_job.get('description', job.job_title)
                   if solr_job
                   else u"This job ({title}) has expired.".format(
                       title=job.job_title))
    html_description = (solr_job.get('html_description', job.job_title)
                        if solr_job
                        else u"This job ({title}) has expired.".format(
                            title=job.job_title))
    body = "\n".join([body, dashes, description])
    html_body = "<br />".join([html_body, dashes, html_description])

    # We reached this point; the data should be good
    email = EmailMultiAlternatives(
        to=[new_to], from_email=from_email, subject=subject,
        body=body, cc=cc, headers=sg_headers)
    email.attach_alternative(html_body, 'text/html')
    for attachment in attachment_data:
        email.attach(*attachment)
    email.send()

    log = {'from_addr': from_email,
           'to_guid': to_guid,
           'buid': job.buid,
           'to_addr': new_to}
    EmailRedirectLog.objects.create(**log)

    return HttpResponse(status=200)


def update_buid(request):
    """
    API for updating business units
    """
    old = request.GET.get('old_buid', None)
    new = request.GET.get('new_buid', None)
    key = request.GET.get('key', None)

    data = {'error': ''}

    if settings.BUID_API_KEY != key:
        data['error'] = 'Unauthorized'
        return HttpResponse(json.dumps(data),
                            content_type='application/json',
                            status=401)

    try:
        old = int(request.GET.get('old_buid', None))
    except (ValueError, TypeError):
        data = {'error': 'Invalid format for old business unit'}
        return HttpResponse(json.dumps(data),
                            content_type='application/json',
                            status=400)

    try:
        new = int(request.GET.get('new_buid', None))
    except (ValueError, TypeError):
        data = {'error': 'Invalid format for new business unit'}
        return HttpResponse(json.dumps(data),
                            content_type='application/json',
                            status=400)

    if CanonicalMicrosite.objects.filter(buid=new) or \
            DestinationManipulation.objects.filter(buid=new):
        data = {'error': 'New business unit already exists'}
        return HttpResponse(json.dumps(data),
                            content_type='application/json',
                            status=400)

    try:
        cm = CanonicalMicrosite.objects.get(buid=old)
    except CanonicalMicrosite.DoesNotExist:
        num_instances = 0
    else:
        num_instances = 1
        cm.buid = new
        cm.save()

    dms = DestinationManipulation.objects.filter(buid=old)
    for dm in dms:
        dm.pk = None
        dm.id = None
        dm.buid = new
        dm.save()
    num_instances += dms.count()

    data.pop('error')
    data['updated'] = num_instances
    data['new_bu'] = new
    return HttpResponse(json.dumps(data),
                        content_type='application/json')


def redirect_404(request):
    return HttpResponseNotFound(loader.render_to_string(
        'redirect/404.html', context_instance=RequestContext(request)))


def redirect_500(request):
    return HttpResponseServerError(loader.render_to_string(
        '500_base.html', context_instance=RequestContext(request)))
