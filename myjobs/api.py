import datetime
from urlparse import urlparse
from urllib import unquote

from django.db import IntegrityError

from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.http import HttpResponse
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

from myjobs.models import User
from mysearches.helpers import validate_dotjobs_url
from mysearches.models import SavedSearch


class UserResource(ModelResource):
    searches = fields.ToManyField('myjobs.api.SavedSearchResource',
                                  'savedsearch_set')

    class Meta:
        filtering = {"email": "exact"}
        queryset = User.objects.all()
        resource_name = 'user'
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        authentication = ApiKeyAuthentication()
        always_return_data = True
        serializer = Serializer(formats=['json', 'jsonp'],
                                content_types={'json': 'application/json',
                                               'jsonp': 'text/javascript'})

    def build_filters(self, filters=None):
        filters.pop('source', '')
        return super(UserResource, self).build_filters(filters)

    def create_response(self, request, data, response_class=HttpResponse,
                        **response_kwargs):
        """
        Intercepts the default create_response(). Checks for existing user
        and creates a new user if one matching the email doesn't exist.

        Creates new JSON formatted "data" based on the success, failure,
        or error in user creation. Returns new data to the default
        create_response().

        """
        email = request.GET.get('email', '')
        if not email:
            data = {'email': 'No email provided'}
            return super(UserResource, self).create_response(
                request, data, response_class=HttpResponse, **response_kwargs)

        try:
            kwargs = {'email': email,
                      'password1': request.GET.get('password', ''),
                      'request': request}
            user, created = User.objects.create_user(send_email=True,
                                                     **kwargs)

            data = {
                'user_created': created,
                'email': email}
            if not created and user.in_reserve:
                user.in_reserve = False
                user.save()
                # TODO: accept all invitations and send password email?
        except IntegrityError:
            data = {'email': 'That username already exists'}

        return super(UserResource, self).create_response(
            request, data, response_class=HttpResponse, **response_kwargs)


class SavedSearchResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        filtering = {"email": "exact", "url": "exact"}
        queryset = SavedSearch.objects.all()
        resource_name = 'savedsearch'
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        authentication = ApiKeyAuthentication()
        always_return_data = True
        serializer = Serializer(formats=['json', 'jsonp'],
                                content_types={'json': 'application/json',
                                               'jsonp': 'text/javascript'})

    def create_response(self, request, data, response_class=HttpResponse,
                        **response_kwargs):
        """
        Intercepts the default create_reponse(). Checks for existing saved
        search matching the user and url. If one doesn't exist, it creates
        a new saved search with daily email and the date/time created in
        the notes.

        Creates new JSON formatted "data" based on the success, failure, or
        error in saved search creation. Returns this data to the default
        create_response().

        """
        # Confirm email was provided, and that the user exists
        email = request.GET.get('email', '')

        if not email:
            data = {'error': 'No email provided'}
            return super(SavedSearchResource, self).create_response(
                request, data, response_class=HttpResponse, **response_kwargs)
        else:
            user = User.objects.get_email_owner(email=email)
            if not user:
                data = {'error': 'No user with email %s exists' % email}
                return super(SavedSearchResource, self).create_response(
                    request, data, response_class=HttpResponse,
                    **response_kwargs)

        # Confirm that url was provided, and that it's a valid .jobs search
        url = request.GET.get('url', '')
        url = unquote(url)

        if not url:
            data = {'error': 'No .JOBS feed provided'}
            return super(SavedSearchResource, self).create_response(
                request, data, response_class=HttpResponse, **response_kwargs)
        else:
            label, feed = validate_dotjobs_url(url, user)
            if not (label and feed):
                data = {'error': 'This is not a valid .JOBS feed'}
                return super(SavedSearchResource, self).create_response(
                    request, data, response_class=HttpResponse,
                    **response_kwargs)

        # Create notes field noting that it was created as current date/time
        now = datetime.datetime.now().strftime('%A, %B %d, %Y %l:%M %p')
        notes = 'Saved on ' + now
        if url.find('//') == -1:
            url = 'http://' + url
        netloc = urlparse(url).netloc
        notes += ' from ' + netloc

        search_args = {'url': url,
                       'label': label,
                       'feed': feed,
                       'user': user,
                       'email': email,
                       'frequency': 'D',
                       'day_of_week': None,
                       'day_of_month': None,
                       'notes': notes}

        # if there's no search for that email/user, create it
        # if it exists and is inactive, activate it
        new_search = False
        try:
            existing_search = SavedSearch.objects.get(user=search_args['user'],
                                            email__iexact=search_args['email'],
                                            url=search_args['url'])
            if existing_search and not existing_search.is_active:
                existing_search.is_active = True
                existing_search.save()

        except SavedSearch.DoesNotExist:
            search = SavedSearch(**search_args)
            search.save()
            search.initial_email()
            new_search = True

        data = {'email': email,
                'frequency': 'D',
                'new_search': new_search}

        return super(SavedSearchResource, self).create_response(
            request, data, response_class=HttpResponse, **response_kwargs)
