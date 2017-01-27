import base64
from collections import defaultdict
import datetime
import json
import logging
from multiprocessing import Process
import urllib2
from urlparse import urlparse, urljoin
import uuid

from django.conf import settings
from django.contrib.auth import logout, authenticate
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.forms import Form, model_to_dict
from django.http import (
    HttpResponse, HttpResponseRedirect, HttpResponseForbidden)
from django.core import serializers
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect, render, Http404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods

from captcha.fields import ReCaptchaField
from impersonate.decorators import allowed_user_required
from impersonate.views import impersonate as impersonate_

from universal.helpers import get_domain
from universal.decorators import restrict_to_staff
from myjobs.decorators import user_is_allowed, requires
from myjobs.forms import (ChangePasswordForm, EditCommunicationForm,
                          CompanyAccessRequestForm, AccessRequestForm)
from myjobs.helpers import expire_login, log_to_jira, get_title_template
from myjobs.models import (Ticket, User, FAQ, CustomHomepage, Role, Activity,
                           CompanyAccessRequest, SecondPartyAccessRequest)
from myprofile.forms import (InitialNameForm, InitialEducationForm,
                             InitialAddressForm, InitialPhoneForm,
                             InitialWorkForm)
from myprofile.models import ProfileUnits, Name
from registration.forms import RegistrationForm, CustomAuthForm
from registration.models import Invitation
from seo.models import SeoSite
from tasks import (process_sendgrid_event, create_jira_ticket,
                   assign_ticket_to_request)
from universal.helpers import get_company_or_404

logger = logging.getLogger(__name__)


class About(TemplateView):
    template_name = "about.html"


class Privacy(TemplateView):
    template_name = "privacy-policy.html"


class Terms(TemplateView):
    template_name = "terms.html"


class CaptchaForm(Form):
    captcha = ReCaptchaField(label="", attrs={'theme': 'white'})


def error_500(request):
    response = render(request, "500.html")
    response.status_code = 500
    return response


def home(request):
    """
    The home page view receives 2 separate Ajax requests, one for the
    registration form and another for the initial profile information form. If
    everything checks out alright and the form saves with no errors, it returns
    a simple string, 'valid', as an HTTP Response, which the front end
    recognizes as a signal to continue with the account creation process. If an
    error occurs, this triggers the jQuery to update the page. The form
    instances with errors must be passed back to the form template it was
    originally from.

    """
    registration_form = RegistrationForm(auto_id=False)
    login_form = CustomAuthForm(auto_id=False)

    name_form = InitialNameForm(prefix="name")
    education_form = InitialEducationForm(prefix="edu")
    phone_form = InitialPhoneForm(prefix="ph")
    work_form = InitialWorkForm(prefix="work")
    address_form = InitialAddressForm(prefix="addr")
    nexturl = request.GET.get('next')
    title_template = get_title_template(nexturl)
    if nexturl:
        nexturl = urllib2.unquote(nexturl)
        nexturl = urllib2.quote(nexturl.encode('utf8'))

    last_ms = request.COOKIES.get('lastmicrosite')
    site_name = ''
    logo_url = ''
    show_registration = True
    if last_ms:
        try:
            last_ms = get_domain(last_ms)
            custom_page = CustomHomepage.objects.get(domain=last_ms)
            logo_url = custom_page.logo_url
            show_registration = custom_page.show_signup_form
            site_name = custom_page.name

        except CustomHomepage.DoesNotExist:
            pass

    data_dict = {'num_modules': len(settings.PROFILE_COMPLETION_MODULES),
                 'registrationform': registration_form,
                 'loginform': login_form,
                 'name_form': name_form,
                 'phone_form': phone_form,
                 'address_form': address_form,
                 'work_form': work_form,
                 'education_form': education_form,
                 'nexturl': nexturl,
                 'logo_url': logo_url,
                 'show_registration': show_registration,
                 'site_name': site_name,
                 'logo_template': title_template,
                 }

    if request.method == "POST":
        if request.POST.get('action') == "register":
            registration_form = RegistrationForm(request.POST, auto_id=False)
            if registration_form.is_valid():
                new_user, created = User.objects.create_user(
                    request=request,
                    send_email=True,
                    **registration_form.cleaned_data)
                user_cache = authenticate(
                    username=registration_form.cleaned_data['email'],
                    password=registration_form.cleaned_data['password1'])
                expire_login(request, user_cache)
                ctx = {}
                ctx['success'] = True
                response = HttpResponse(json.dumps(ctx))
                response.set_cookie('myguid', new_user.user_guid,
                                    expires=365*24*60*60, domain='.my.jobs')
                response.delete_cookie('loggedout')
                return response
            else:
                return HttpResponse(json.dumps(
                    {'errors': registration_form.errors.items()}))

        elif request.POST.get('action') == "login":
            login_form = CustomAuthForm(data=request.POST)
            if login_form.is_valid():
                expire_login(request, login_form.get_user())

                url = request.POST.get('nexturl')

                # Boolean for activation login page to show initial forms
                # again or not
                has_units = False
                if len(login_form.get_user().profileunits_set.all()) > 0:
                    has_units = True

                response_data = {
                    'validation': 'valid', 'url': url,
                    'units': has_units,
                    'gravatar_url': login_form.get_user().get_gravatar_url(
                        size=100)}
                response = HttpResponse(json.dumps(response_data))
                response.set_cookie('myguid', login_form.get_user().user_guid,
                                    expires=365*24*60*60, domain='.my.jobs')
                response.delete_cookie('loggedout')
                return response
            else:
                return HttpResponse(json.dumps({'errors':
                                                login_form.errors.items()}))

        elif request.POST.get('action') == "save_profile":
            name_form = InitialNameForm(request.POST, prefix="name",
                                        user=request.user)
            if not name_form.changed_data:
                name_form = InitialNameForm(prefix="name")

            education_form = InitialEducationForm(request.POST, prefix="edu",
                                                  user=request.user)
            if not education_form.changed_data:
                education_form = InitialEducationForm(prefix="edu")

            phone_form = InitialPhoneForm(request.POST, prefix="ph",
                                          user=request.user)
            if not phone_form.changed_data:
                phone_form = InitialPhoneForm(prefix="ph")

            work_form = InitialWorkForm(request.POST, prefix="work",
                                        user=request.user)
            if not work_form.changed_data:
                work_form = InitialWorkForm(prefix="work")

            address_form = InitialAddressForm(request.POST, prefix="addr",
                                              user=request.user)
            if not address_form.changed_data:
                address_form = InitialAddressForm(prefix="addr")

            forms = [name_form, education_form, phone_form, work_form,
                     address_form]
            valid_forms = [form for form in forms if form.is_valid()]
            invalid_forms = []
            for form in forms:
                if form.changed_data and not form.is_valid():
                    invalid_forms.append(form)

            if not invalid_forms:
                for form in valid_forms:
                    if form.changed_data:
                        form.save(commit=False)
                        form.user = request.user
                        form.save_m2m()
                return HttpResponse('valid')
            else:
                return render_to_response('includes/initial-profile-form.html',
                                          {'name_form': name_form,
                                           'phone_form': phone_form,
                                           'address_form': address_form,
                                           'work_form': work_form,
                                           'education_form': education_form},
                                          context_instance=RequestContext(
                                              request))

    return render_to_response('index.html', data_dict, RequestContext(request))


def contact_faq(request):
    """
    Grabs FAQ and orders them by alphabetical order on question.

    """
    faq = FAQ.objects.filter(is_visible=True).order_by('question')
    if faq.count() <= 0:
        return HttpResponseRedirect(reverse('contact'))
    data_dict = {'faq': faq}
    return render_to_response('contact-faq.html',
                              data_dict, RequestContext(request))


def contact(request):
    if request.POST:
        name = request.POST.get('name')
        contact_type = request.POST.get('type')
        reason = request.POST.get('reason')
        from_email = request.POST.get('email')
        phone_num = request.POST.get('phone')
        comment = request.POST.get('comment')
        form = CaptchaForm(request.POST)
        if form.is_valid():
            components = []
            component_ids = {'My.jobs Error': {'id': '12903'},
                             'Job Seeker': {'id': '12902'},
                             'Employer': {'id': '12900'},
                             'Partner': {'id': '12901'},
                             'Request Demo': {'id': '13900'}}
            if component_ids.get(reason):
                components.append(component_ids.get(reason))
            components.append(component_ids.get(contact_type))
            issue_dict = {
                'summary': '%s - %s' % (reason, from_email),
                'description': '%s' % comment,
                'issuetype': {'name': 'Task'},
                'customfield_10400': str(name),
                'customfield_10401': str(from_email),
                'customfield_10402': str(phone_num),
                'components': components}

            subject = 'Contact My.jobs by a(n) %s' % contact_type
            body = """
                   Name: %s
                   Is a(n): %s
                   Email: %s

                   %s
                   """ % (name, contact_type, from_email, comment)

            to_jira = log_to_jira(subject, body, issue_dict, from_email)
            if to_jira:
                time = datetime.datetime.now().strftime(
                    '%A, %B %d, %Y %l:%M %p')
                return HttpResponse(json.dumps({'validation': 'success',
                                                'name': name,
                                                'c_type': contact_type,
                                                'reason': reason,
                                                'c_email': from_email,
                                                'phone': phone_num,
                                                'comment': comment,
                                                'c_time': time}))
            else:
                return HttpResponse('success')
        else:
            return HttpResponse(json.dumps({'validation': 'failed',
                                            'errors': form.errors.items()}))
    else:
        form = CaptchaForm()
        data_dict = {'form': form}
    return render_to_response('contact.html', data_dict,
                              RequestContext(request))


@user_is_allowed()
@user_passes_test(User.objects.not_disabled)
def edit_account(request):
    user = request.user
    obj = User.objects.get(id=user.id)
    change_password = False

    if user.is_verified:
        communication_form = EditCommunicationForm(user=user, instance=obj)
    else:
        communication_form = None
    password_form = ChangePasswordForm(user=user)

    if request.user.password_change:
        change_password = True

    ctx = {
        'user': user,
        'communication_form': communication_form,
        'password_form': password_form,
        'change_password': change_password,
    }

    if request.method == "POST":
        obj = User.objects.get(id=request.user.id)
        if 'communication' in request.REQUEST:
            form = EditCommunicationForm(user=request.user, instance=obj,
                                         data=request.POST)
            if form.is_valid():
                form.save()
                ctx['communication_form'] = form
                ctx['message_body'] = ('Communication Settings have been '
                                       'updated successfully.')
                ctx['messagetype'] = 'success'
                template = '%s/edit-account.html' % settings.PROJECT
                return render_to_response(template, ctx,
                                          RequestContext(request))
            else:
                ctx['communication_form'] = form
                template = '%s/edit-account.html' % settings.PROJECT
                return render_to_response(template, ctx,
                                          RequestContext(request))

        elif 'password' in request.REQUEST:
            form = ChangePasswordForm(user=request.user, data=request.POST)
            if form.is_valid():
                request.user.password_change = False
                request.user.save()
                form.save()
                ctx['password_form'] = form
                ctx['message_body'] = ('Password Settings have been '
                                       'updated successfully.')
                ctx['messagetype'] = 'success'
                template = '%s/edit-account.html' % settings.PROJECT
                return render_to_response(template, ctx,
                                          RequestContext(request))
            else:
                ctx['password_form'] = form
                template = '%s/edit-account.html' % settings.PROJECT
                return render_to_response(template, ctx,
                                          RequestContext(request))
        else:
            raise Http404("myjobs.views.edit_account: request is not POST")

    return render_to_response('%s/edit-account.html' % settings.PROJECT, ctx,
                              RequestContext(request))


@user_passes_test(User.objects.not_disabled)
def delete_account(request):
    email = request.user.email
    request.user.delete()

    template = '%s/delete-account-confirmation.html' % settings.PROJECT
    ctx = {'email': email}

    return render_to_response(template, ctx, RequestContext(request))


@user_passes_test(User.objects.not_disabled)
def disable_account(request):
    user = request.user
    email = user.email
    user.disable()
    logout(request)

    template = '%s/disable-account-confirmation.html' % settings.PROJECT
    ctx = {'email': email}

    return render_to_response(template, ctx, RequestContext(request))


@csrf_exempt
def batch_message_digest(request):
    """
    Used by SendGrid to POST batch events.

    Accepts a POST request containing a batch of events from SendGrid. A batch
    of events is a series of JSON strings separated by new lines (Version 1 and
    2) or as well formed JSON (Version 3)

    Creates a celery task that adds these events to the EmailLog.

    """
    if 'HTTP_AUTHORIZATION' in request.META:
        method, details = request.META['HTTP_AUTHORIZATION'].split()
        if method.lower() == 'basic':
            # login_info is intended to be a base64-encoded string in the
            # format "email:password" where email is a urlquoted string
            login_info = base64.b64decode(details).split(':')
            if len(login_info) == 2:
                login_info[0] = urllib2.unquote(login_info[0])
                user, password = login_info

                if (user == settings.SENDGRID_BATCH_POST_USER and
                        password == settings.SENDGRID_BATCH_POST_PASSWORD):

                    process_sendgrid_event.delay(request.body)
                    return HttpResponse(status=200)
    return HttpResponse(status=403)


@user_is_allowed(pass_user=True)
def continue_sending_mail(request, user=None):
    """
    Updates the user's last response time to right now.
    Allows the user to choose to continue receiving emails if they are
    inactive.
    """
    user = user or request.user
    user.last_response = datetime.date.today()
    user.save()
    return redirect('/')


def check_name_obj(user):
    """
    Utility function to process and return the user name object.

    Inputs:
    :user:  request.user object

    Returns:
    :initial_dict: Dictionary object with updated name information
    """
    initial_dict = model_to_dict(user)
    try:
        name = Name.objects.get(user=user, primary=True)
    except Name.DoesNotExist:
        name = None
    if name:
        initial_dict.update(model_to_dict(name))
    return initial_dict


@user_is_allowed(pass_user=True)
def unsubscribe_all(request, user=None):
    user = user or request.user
    user.opt_in_myjobs = False
    user.save()

    return render_to_response('myjobs/unsubscribe_all.html',
                              context_instance=RequestContext(request))


def cas(request):
    redirect_url = request.GET.get('redirect_url', 'http://www.my.jobs/')
    user = request.user

    if not user or user.is_anonymous():
        guid = request.COOKIES.get('myguid')
        try:
            user = User.objects.get(user_guid=guid)
        except User.DoesNotExist:
            pass
    if not user or user.is_anonymous():
        response = redirect("https://secure.my.jobs/?next=%s" %
                            redirect_url)
    else:
        ticket = Ticket()
        try:
            ticket.ticket = uuid.uuid4()
            ticket.session_id = request.session.session_key
            ticket.user = request.user
            ticket.save()
        except IntegrityError:
            return cas(request)
        except Exception, e:
            logging.error("cas: %s" % e)
            response = redirect("https://secure.my.jobs/?next=%s" %
                                redirect_url)
        else:
            if '?' in redirect_url:
                response = redirect("%s&ticket=%s&uid=%s" %
                                    (redirect_url, ticket.ticket,
                                     ticket.user.user_guid))
            else:
                response = redirect("%s?ticket=%s&uid=%s" %
                                    (redirect_url, ticket.ticket,
                                     ticket.user.user_guid))
    caller = urlparse(redirect_url)
    try:
        page = CustomHomepage.objects.get(domain=caller.netloc.split(":")[0])
        response.set_cookie(key='lastmicrosite',
                                value="%s://%s" % (caller.scheme,
                                                   caller.netloc),
                                max_age=30 * 24 * 60 * 60,
                                domain='.my.jobs')
        response.set_cookie(key='lastmicrositename',
                                value=page.name,
                                max_age=30 * 24 * 60 * 60,
                                domain='.my.jobs')
    except CustomHomepage.DoesNotExist:
        pass

    return response


def topbar(request):
    callback = request.REQUEST.get('callback')
    use_v2 = request.REQUEST.get('v2', 0)
    user = request.user
    impersonating = request.REQUEST.get('impersonating')

    if not user or user.is_anonymous():
        # Ensure that old myguid cookies can be handled correctly
        guid = request.COOKIES.get('myguid', '').replace('-', '')
        try:
            user = User.objects.get(user_guid=guid)
        except User.DoesNotExist:
            pass

    if not user or user.is_anonymous():
        user = None

    ctx = {'user': user, 'impersonating': impersonating == u'true'}

    response = HttpResponse(content_type='text/javascript')

    caller = request.REQUEST.get('site', '')
    if caller:
        max_age = 30 * 24 * 60 * 60
        last_name = request.REQUEST.get('site_name', caller)
        response.set_cookie(key='lastmicrosite',
                            value=caller,
                            max_age=max_age,
                            domain='.my.jobs')
        response.set_cookie(key='lastmicrositename',
                            value=last_name,
                            max_age=max_age,
                            domain='.my.jobs')
        ctx['current_microsite_name'] = last_name
        ctx['current_microsite_url'] = caller
        # Switch between version 1 and 2 topbar template
    if use_v2:
        template_string = 'includes/topbar_v2.html'
    else:
        template_string = 'includes/topbar.html'

    html = render_to_response(template_string, ctx,
                              RequestContext(request))
    response.content = "%s(%s)" % (callback, json.dumps(html.content))

    return response


@requires("read role")
def manage_users(request):
    """
    View for manage users
    """
    company = get_company_or_404(request)

    ctx = {
        "company": company
        }

    return render_to_response('manageusers/index.html',
                              ctx,
                              RequestContext(request))


@require_http_methods(['GET'])
@requires("read role")
def api_get_activities(request):
    """
    GET /manage-users/api/activities/
    Retrieves all activities
    """

    company = get_company_or_404(request)

    # group activities by their app access
    activities = defaultdict(list)
    for activity in company.activities.order_by('app_access__pk'):
        activities[activity.app_access.name].append({
            'id': activity.pk,
            'name': unicode(activity),
            'description': activity.description,
            'display_name': activity.display_name})

    return HttpResponse(json.dumps(activities), mimetype='application/json')


# TODO: rename this to api_get_roles once the roles page is converted
@require_http_methods(['GET'])
@requires("read role")
def api_get_all_roles(request):
    """
    GET /manage-users/api/roles/all/
    Retrieves all roles associated with a company

    """
    company = get_company_or_404(request)

    ctx = {
        role.id: {
            'name': role.name,
            'activities': [{
                'id': activity.pk,
                'name': activity.name,
                'appAccess': activity.app_access.name,
                'description': activity.description
            } for activity in role.activities.all()]
        }
        for role in company.role_set.select_related('activities').all()
    }

    return HttpResponse(json.dumps(ctx), mimetype='application/json')


@requires("read role")
def api_get_roles(request):
    """
    GET /manage-users/api/roles/
    Retrieves all roles associated with a company
    """

    company = get_company_or_404(request)

    # Get all roles for this company
    roles = Role.objects.filter(company=company)

    # Get all apps this company can access
    app_access_for_company = company.app_access.all()

    # Retrieve all available_activities for this company
    available_activities = (Activity
                            .objects
                            .filter(app_access__in = app_access_for_company))

    # Retrieve users that can be assigned to these roles. In other words,
    # users already assigned to roles associated with this company
    available_users = []
    for user in User.objects.filter(roles__in=roles).distinct():
        user_more = {}
        user_more['id'] = user.id
        user_more['name'] = user.email
        available_users.append(user_more)

    # Loop through and format all assigned roles_formatted
    roles_formatted = []
    for role in roles:
        role_id = role.id
        role_name = role.name

        # Build list of apps this company can access
        # For each app, build list of:
        #   app_access_name
        #   available_activities
        #   assigned_activities
        activities = []

        for app_access in app_access_for_company:
            activity = {}
            activity['app_access_name'] = app_access.name

            activity['available_activities'] = []
            # Loop through all activities associated with this particular app_access
            for available_activity in available_activities.filter(app_access=app_access.id):
                display_name = unicode(available_activity)
                available_activity_more = {}
                available_activity_more['id'] = available_activity.id
                available_activity_more['name'] = display_name
                activity['available_activities'].append(available_activity_more)

            activity['assigned_activities'] = []
            for assigned_activity in role.activities.filter(app_access=app_access.id):
                display_name = unicode(assigned_activity)
                assigned_activity_more = {}
                assigned_activity_more['id'] = assigned_activity.id
                assigned_activity_more['name'] = display_name
                activity['assigned_activities'].append(assigned_activity_more)

            activities.append(activity)

        # Retrieve users already assigned to this particular role
        assigned_users = []
        # These are users with this role
        users = User.objects.filter(roles__id=role_id).distinct()
        for user in users:
            user_more = {}
            user_more['id'] = user.id
            user_more['name'] = user.email
            assigned_users.append(user_more)

        # Assemble role object
        role_formatted = dict(
            role_id=int(role_id),
            role_name=role_name,
            available_users=available_users,
            assigned_users=assigned_users,
            activities=activities
        )

        # Add formatted role to growing list
        roles_formatted.append(role_formatted)

    return HttpResponse(json.dumps(roles_formatted),
                        mimetype='application/json')


@require_http_methods(['GET'])
@requires('read role')
def api_get_specific_role(request, role_id=0):
    """
    GET /manage-users/api/roles/NUMBER
    Retrieves specific role
    """
    ctx = {}

    # Check if role exists
    if Role.objects.filter(id=role_id).exists() is False:
        ctx["success"] = "false"
        ctx["message"] = "Role does not exist."
        return HttpResponse(json.dumps(ctx),
                            content_type="application/json")

    company = get_company_or_404(request)

    role_edited = Role.objects.get(pk=role_id)
    role_name = role_edited.name

    # Retrieve users that can be assigned to this role. In other words, users
    # already assigned to roles associated with this company
    available_users_as_queries = []
    roles = Role.objects.filter(company=company)
    for role in roles:
        role_id_temp = role.id
        users = User.objects.filter(roles__id=role_id_temp).distinct()
        for user in users:
            # Make sure available_users is distinct
            if user not in available_users_as_queries:
                available_users_as_queries.append(user)
    # available_users should be distinct list of user queries
    available_users = []
    for user in available_users_as_queries:
        user_more = {}
        user_more['id'] = user.id
        user_more['name'] = user.email
        available_users.append(user_more)

    # Retrieve users already assigned to this particular role
    assigned_users = []
    users = User.objects.filter(roles__id=role_id).distinct()
    for user in users:
        user_more = {}
        user_more['id'] = user.id
        user_more['name'] = user.email
        assigned_users.append(user_more)

    # Build list of apps this company can access
    # For each app, build list of:
    #   app_access_name
    #   available_activities
    #   assigned_activities
    activities = []
    # Retrieve all available_activities for this company
    available_activities = Activity.objects.filter(app_access__in=company.app_access.all())

    for app_access in company.app_access.all():
        activity = {}
        activity['app_access_name'] = app_access.name

        activity['available_activities'] = []
        for available_activity in available_activities.filter(app_access=app_access.id):
            display_name = unicode(available_activity)
            available_activity_more = {}
            available_activity_more['id'] = available_activity.id
            available_activity_more['name'] = display_name
            activity['available_activities'].append(available_activity_more)

        activity['assigned_activities'] = []
        for assigned_activity in role_edited.activities.filter(app_access=app_access.id):
            display_name = unicode(assigned_activity)
            assigned_activity_more = {}
            assigned_activity_more['id'] = assigned_activity.id
            assigned_activity_more['name'] = display_name
            activity['assigned_activities'].append(assigned_activity_more)

        activities.append(activity)

    json_obj = dict(
        role_id = int(role_id),
        role_name = role_name,
        available_users = available_users,
        assigned_users = assigned_users,
        activities = activities,
    )

    return HttpResponse(json.dumps(json_obj),
                        mimetype='application/json')


@requires('create role')
def api_create_role(request):
    """
    POST /manage-users/api/roles/create
    Creates a new role

    Inputs:
    :role_name:                 name of role
    :assigned_activities:       activities assigned to this role
    :assigned_users:            users assigned to this role

    Returns:
    :success:                   boolean
    """

    ctx = {}

    if request.method != "POST":
        ctx["success"] = "false"
        ctx["message"] = "POST method required."
        return HttpResponse(json.dumps(ctx),
                            content_type="application/json")
    else:
        company = get_company_or_404(request)

        if request.POST.get("role_name", ""):
            role_name = request.POST['role_name']

        # Role names must be unique
        matching_roles = Role.objects.filter(name=role_name, company=company)
        if matching_roles.exists():
            ctx["success"] = "false"
            ctx["message"] = "Another role with this name already exists."
            return HttpResponse(json.dumps(ctx),
                                content_type="application/json")

        activity_ids = []
        if request.POST.getlist("assigned_activities[]"):
            activity_ids = request.POST.getlist("assigned_activities[]")
        # At least one activity must be selected
        if not activity_ids:
            ctx["success"] = "false"
            ctx["message"] = "Each role must have at least one activity."
            return HttpResponse(json.dumps(ctx),
                                content_type="application/json")

        # User objects have roles
        selected_users = request.POST.getlist("assigned_users[]", [])

        # Create Role
        new_role = Role.objects.create(name=role_name, company_id=company.id)

        # Assign activities to this new role
        new_role.activities.add(*activity_ids)

        # Add role to relevant users
        users = User.objects.filter(email__in=selected_users)

        for user in users:
            user.roles.add(new_role.id)
            user.send_invite(user.email, company, new_role.name)

        ctx["success"] = "true"
        return HttpResponse(json.dumps(ctx),
                            content_type="application/json")


@requires('update role')
def api_edit_role(request, role_id=0):
    """
    POST /manage-users/api/roles/edit
    Edits an existing role

    Inputs:
    :role_id:                   unique id of role
    :role_name:                 name of role
    :assigned_activites:        PKs of activities assigned to this role
    :assigned_users:            users assigned to this role

    Returns:
    :success:                   boolean
    """
    ctx = {}
    if request.method != "POST":
        ctx["success"] = "false"
        ctx["message"] = "POST method required."
        return HttpResponse(json.dumps(ctx), content_type="application/json")
    else:
        # Check if role exists
        if Role.objects.filter(id=role_id).exists() is False:
            ctx["success"] = "false"
            ctx["message"] = "Role does note exist."
            return HttpResponse(json.dumps(ctx),
                                content_type="application/json")

        company = get_company_or_404(request)

        # Check if the company the user is associated with manages this role
        role = Role.objects.get(pk=role_id)
        if role.company.id != company.id:
            ctx["success"] = "false"
            ctx["message"] = "The company you are associated with does not \
                              manage this role."
            return HttpResponse(json.dumps(ctx),
                                content_type="application/json")

        # INPUT - role_name
        role_name = request.POST.get("role_name", "")
        # Role names must be unique
        matching_roles = Role.objects.filter(
            name=role_name,
            company=company).exclude(pk=role_id)

        if matching_roles.exists():
            ctx["success"] = "false"
            ctx["message"] = "Another role with this name already exists."
            return HttpResponse(json.dumps(ctx),
                                content_type="application/json")

        activity_ids = []
        if request.POST.getlist("assigned_activities[]"):
            activity_ids = request.POST.getlist("assigned_activities[]")

        # At least one activity must be selected
        if not activity_ids:
            ctx["success"] = "false"
            ctx["message"] = "At least one activity must be assigned."
            return HttpResponse(json.dumps(ctx),
                                content_type="application/json")
        # INPUT - assigned_users
        assigned_users_emails = request.POST.getlist("assigned_users[]", "")

        # EDIT ROLE - Name
        if role_name != "":
            if role.name != role_name:
                role.name = role_name
                role.save()

        # EDIT ROLE - Activities
        # Remove any currently assigned activities not in new
        # assigned_activites list
        activities_currently_assigned = role.activities.all()
        for activity_currently_assigned in activities_currently_assigned:
            if activity_currently_assigned.id not in activity_ids:
                role.activities.remove(activity_currently_assigned.id)
                role.save()
        # Add activities in new assigned_activites list
        for activity_id in activity_ids:
            role.activities.add(activity_id)
            role.save()
        # EDIT ROLE - Users assigned to this role
        # Loop through all users. Should each be assigned this role? Or not?
        existing_users = User.objects.filter(roles__id__exact=role_id)
        new_users = User.objects.filter(email__in=assigned_users_emails)
        for user in existing_users.exclude(pk__in=new_users.values("pk")):
            user.roles.remove(role_id)
        for user in new_users.exclude(pk__in=existing_users.values("pk")):
            user.roles.add(role_id)
            user.send_invite(user.email, company, role.name)
        ctx["success"] = "true"
        return HttpResponse(json.dumps(ctx),
                            content_type="application/json")


@requires('delete role')
def api_delete_role(request, role_id=0):
    """
    POST /manage-users/api/roles/delete/NUMBER
    Deletes a role

    Inputs:
    :role_id:                   id of role

    Returns:
    :success:                   boolean
    """
    ctx = {}

    if request.method != "DELETE":
        ctx["success"] = "false"
        ctx["message"] = "DELETE method required."
        return HttpResponse(json.dumps(ctx), content_type="application/json")

    else:
        company = get_company_or_404(request)

        # Check if role exists
        if Role.objects.filter(id=role_id).exists() is False:
            ctx["success"] = "false"
            return HttpResponse(json.dumps(ctx),
                                content_type="application/json")

        # Check that company manages this role and can therefore delete it
        company_id_to_delete = Role.objects.filter(id=role_id)[0].company.id
        if company.id != company_id_to_delete:
            ctx["success"] = "false"
            return HttpResponse(json.dumps(ctx),
                                content_type="application/json")

        Role.objects.filter(id=role_id).delete()
        if Role.objects.filter(id=32).exists() is False:
            ctx["success"] = "true"
            return HttpResponse(json.dumps(ctx),
                                content_type="application/json")

        ctx["success"] = "false"
        ctx["message"] = "Role not deleted."
        return HttpResponse(json.dumps(ctx),
                            content_type="application/json")


@require_http_methods(['GET'])
@requires('read user')
def api_get_users(request):
    """
    GET /manage-users/api/users/
    Retrieves all users associated with a company

    """
    company = get_company_or_404(request)
    users = User.objects.select_related('roles').filter(roles__company=company)
    ctx = {}
    for user in users:
        last_invitation = ""
        if not user.is_verified:
            invitations = Invitation.objects.filter(
                invitee_email=user.email).order_by("-invited")
            if invitations:
                last_invitation = invitations.first().invited.strftime(
                    "%Y-%m-%d")

        ctx[user.pk] = {
            'email': user.email,
            'isVerified': user.is_verified,
            'lastInvitation': last_invitation,
            'roles': list(user.roles.filter(company=company).values_list(
                'name', flat=True))
        }

    return HttpResponse(json.dumps(ctx), content_type="application/json")


@require_http_methods(['POST'])
@requires('update user')
def api_edit_user(request, user_id=0):
    """
    GET /manage-users/api/users/NUMBER
    Retrieves specific user

    """
    company = get_company_or_404(request)
    user = User.objects.filter(pk=user_id).first()
    add = request.POST.getlist('add')
    remove = request.POST.getlist('remove')
    new_roles = []
    is_last_admin = False

    ctx = {'errors': []}

    if user:
        current_roles = list(user.roles.values_list('name', flat=True))
        new_roles = set(current_roles + add) - set(remove)
        is_last_admin = list(company.admins) == [user]
    else:
        ctx['errors'].append('User does not exist.')

    if not ctx['errors'] and not new_roles:
        # Somehow, the API caused all roles to be removed from a user, which in
        # effect removes that user from the company
        ctx['errors'].append('Operation failed, as completing it would have '
                             'removed the user from the company. Is another '
                             'Admin also editing users?')

    # Since new_roles is empty, if there is only one admin, we'd be
    # removing them from the company, which would prevent anyone from
    # modifying users for the company
    if is_last_admin and 'Admin' not in new_roles:
        ctx['errors'].append('Operation failed, as completing it would have '
                             'removed the last Admin from the company. Is '
                             'another Admin also editing users?')

    if user and not ctx['errors']:
        ctx['added'] = add
        ctx['removed'] = remove

        user.roles = Role.objects.filter(
            company=company, name__in=new_roles)

    return HttpResponse(json.dumps(ctx), content_type="application/json")


@require_http_methods(['POST'])
@requires('create user')
def api_add_user(request):
    """
    POST /manage-users/api/user/add/
    Creates a new user

    Inputs:
        :email: user email
        :roles: roles assigned to this user

    """
    company = get_company_or_404(request)
    email = request.POST.get('email')
    roles = request.POST.getlist('roles')
    user = User.objects.get_email_owner(email=email)
    ctx = {'errors': []}

    if roles:
        if user:
            new_roles = set(roles) - set(user.roles.filter(
                company=company).values_list('name', flat=True))

            user.roles.add(*Role.objects.filter(
                company=company, name__in=new_roles))
        else:
            new_roles = roles

        for role in new_roles:
            request.user.send_invite(email, company, role)

        ctx['roles'] = list(new_roles)
        ctx['invited'] = bool(new_roles)
    else:
        ctx['invited'] = False
        ctx['errors'].append(
            "Each user must be assigned to at least one role.")

    return HttpResponse(json.dumps(ctx), mimetype='application/json')


@require_http_methods(['DELETE'])
@requires('delete user')
def api_remove_user(request, user_id=0):
    """
    DELETE /manage-users/api/users/delete/NUMBER
    Removes user from roles managed by current company

    Inputs:
    :user_id:                   id of user

    """
    company = get_company_or_404(request)
    user = User.objects.filter(pk=user_id).first()
    ctx = {'errors': []}

    if list(company.admins) == [user]:
        ctx['errors'].append('Operation failed, as completing it would '
                             'have removed the last Admin from the '
                             'company. Is another Admin also editing '
                             'users?')
    else:
        user.roles.remove(*user.roles.filter(company=company))

    return HttpResponse(json.dumps(ctx), mimetype='application/json')


def request_company_access(request):
    """
    User-Facing view for a user to request access to a company.

    Methods:
        :GET: Shows the request form, which only requires that a company name
              be entered. That company need not map to an actual company.
        :POST: Creates a CompanyAccessRequest, spawns a task which creates a
               JIRA ticket to track the request, and displays the unhashed
               version of the access code to the user.
    """
    if request.user.is_anonymous():
        return HttpResponseRedirect(
            reverse('login') + "?next=/request-company-access")

    ctx = {}
    if request.method == 'POST':
        form = CompanyAccessRequestForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data['company_name']
            access_request, code = CompanyAccessRequest.objects.create_request(
                company_name, request.user)
            ctx['access_code'] = code

            # create a jira ticket
            summary = "Company access requested"
            summary = "company admin request - %s - %s" % (
                access_request.company_name, access_request.requested_by.email)
            description = ("{user} has requested admin access for the company "
                           "{company}. Please contact {company} and obtain the "
                           "verification code provided to {user}. You may "
                           "then enter this code in the admin: {url}")

            # base url will already have a trailing slash
            url = "{base_url}{pk}/".format(
                base_url=urljoin(
                    settings.ABSOLUTE_URL,
                    reverse("admin:myjobs_companyaccessrequest_changelist")),
                pk=access_request.pk)

            description = description.format(
                user=access_request.requested_by.email,
                company=access_request.company_name,
                url=url)

            # asynchronously create a jira ticket and assign it to the access
            # request so that the user doesn't have to wait on a response
            key = create_jira_ticket.delay(
                summary, description,
                project="MEMBERSUP",
                watcher_group="admin-request-watchers",
                components=["admin request"])
            # asynchronously tie that ckreated ticket back to the access
            # request
            assign_ticket_to_request.delay(key, access_request)
    else:
        form = CompanyAccessRequestForm()

    ctx['form'] = form

    return render_to_response(
        'myjobs/request_company_access.html', ctx, RequestContext(request))


@allowed_user_required
def impersonate(request, uid, *args, **kwargs):
    """
    This view is hit by a staff user after a second party access request is
    approved by the target. It starts the request and then redirects to "/"

    """
    account_owner = User.objects.filter(pk=uid).first()
    if account_owner:
        access_request = SecondPartyAccessRequest.objects.filter(
            second_party=request.user,
            account_owner=account_owner,
            accepted=True,
            session_started__isnull=True,
            expired=False).first()
        if access_request:
            return impersonate_(request, uid=uid, *args, **kwargs)
    return HttpResponseForbidden()


@user_is_allowed()
def process_access_request(request, access_id, accepted):
    """
    The target of a second party access request will hit this view to
    approve or reject a given request.
    """
    access_request = SecondPartyAccessRequest.objects.filter(
        account_owner=request.user, pk=access_id,
        acted_on__isnull=True, expired=False).first()
    if access_request:
        context = {
            'access_request': access_request,
            'second_party_name': access_request.second_party.get_full_name(
                default=access_request.second_party_email)}
        if not (access_request.acted_on or access_request.expired):
            context['new'] = True
            access_request.accepted = accepted
            access_request.acted_on = datetime.datetime.now()
            access_request.save()
            access_request.notify_acceptance()
        return render_to_response('myjobs/approve_access_request.html',
                                  context, RequestContext(request))
    else:
        return HttpResponseForbidden()


@allowed_user_required
def request_account_access(request, uid):
    """
    Allows a staff user to input the reason for requesting account access.
    """
    user = User.objects.get(pk=uid)
    admin_view = 'admin:myjobs_user_changelist'
    if user.is_staff or user.is_superuser:
        # This is handled prettier in the action itself. The presence of this
        # check here is to ensure one can't manually craft a post.
        return redirect(admin_view)
    if request.method == 'POST':
        form = AccessRequestForm(request.POST)
        if form.is_valid():
            # Try to intelligently determine the site we're requesting access
            # on. We may be somewhere without certain middleware (settings.SITE
            # may not be populated) or running locally on runserver.
            domains = [request.get_host()]
            if ':' in domains[0]:
                domains.append(domains[0].split(':')[0])
            site = SeoSite.objects.filter(domain__in=domains).first()
            if site is None:
                site = SeoSite.objects.get(domain='secure.my.jobs')
            SecondPartyAccessRequest.objects.create(
                account_owner=user, second_party=request.user, site=site,
                reason=form.cleaned_data['reason'])
            return redirect(admin_view)
    else:
        form = AccessRequestForm()

    return render_to_response('myjobs/access_request.html',
                              {'form': form, 'uid': uid,
                               'full_name': user.get_full_name(
                                   default=user.email)},
                              RequestContext(request))
