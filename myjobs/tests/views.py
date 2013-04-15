from importlib import import_module
from datetime import timedelta
import time

from django.conf import settings
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test.client import Client
from django.test import TestCase

from myjobs.forms import *
from myjobs.models import User
from myjobs.tests.factories import *

from myprofile.models import *
from registration.forms import *
from registration.models import ActivationProfile
from registration import signals as custom_signals

class TestClient(Client):
    """
    Custom test client that decouples testing from the authentication bits
    """
    
    def login_user(self, user):
        if not 'django.contrib.sessions' in settings.INSTALLED_APPS:
            raise AssertionError("Unable to login without django.contrib.sessions in INSTALLED_APPS")
        user.backend = "%s.%s" % ("django.contrib.auth.backends",
                                  "ModelBackend")
        engine = import_module(settings.SESSION_ENGINE)

        # Create a fake request to store login details.
        request = HttpRequest()
        if self.session:
            request.session = self.session
        else:
            request.session = engine.SessionStore()
        login(request, user)

        # Set the cookie to represent the session.
        session_cookie = settings.SESSION_COOKIE_NAME
        self.cookies[session_cookie] = request.session.session_key
        cookie_data = {
            'max-age': None,
            'path': '/',
            'domain': settings.SESSION_COOKIE_DOMAIN,
            'secure': settings.SESSION_COOKIE_SECURE or None,
            'expires': None,
        }
        self.cookies[session_cookie].update(cookie_data)

        # Save the session values.
        request.session.save()

class MyJobsViewsTests(TestCase):
    def setUp(self):
        super(MyJobsViewsTests, self).setUp()
        self.user = UserFactory()
        self.client = TestClient()
        self.client.login_user(self.user)
        self.events = ['open', 'delivered', 'click']
        
    def test_edit_account_success(self):
        resp = self.client.post(reverse('edit_basic'),
                                    data={'given_name': 'Alice',
                                          'family_name': 'Smith',
                                          'gravatar': 'alice@example.com',
                                          'opt_in_myjobs': True}, follow=True)
        name = Name.objects.get(user=resp.context['user'],primary=True)
        self.assertRedirects(resp, 'http://testserver%s' % '/edit/basic?saved=success')
        self.assertEqual(name.given_name, 'Alice')
        self.assertEqual(name.family_name, 'Smith')
        self.assertEqual(resp.context['user'].opt_in_myjobs, True)

    def test_change_password_success(self):
        resp = self.client.post(reverse('edit_password'),
                                    data={'password1': 'secret',
                                          'password2': 'secret',
                                          'new_password': 'new'}, follow=True)
        self.assertRedirects(resp, 'http://testserver%s' % '/edit/password?saved=success')
        self.assertTrue(resp.context['user'].check_password('new'))

    def test_change_password_failure(self):
        resp = self.client.post(reverse('edit_password'),
                                    data={'password1': 'secret',
                                          'password2': 'secretzzzz',
                                          'new_password': 'new'}, follow=True)
        self.failIf(resp.context['form'].is_valid())
        self.assertFormError(resp, 'form', field=None,
                             errors=u"The two password fields didn't match.")

    def test_partial_successful_profile_form(self):
        resp = self.client.post(reverse('home'),
                                data={'name-given_name': 'Alice',
                                      'name-family_name': 'Smith',
                                      'name-primary':False,
                                      'action':'save_profile'}, follow=True)
        self.assertEquals(resp.content, 'valid')
        
    def test_complete_successful_profile_form(self):
        # Form with only some sections completely filled out should
        # save successfully 
        resp = self.client.post(reverse('home'),
                                data={'name-given_name': 'Alice',
                                      'name-family_name': 'Smith',
                                      'name-primary':False,
                                      'education-organization_name': 'Stanford University',
                                      'education-degree_date': '2012-01-01',
                                      'education-education_level_code': 6,
                                      'education-degree_major': 'Basket Weaving',
                                      'employmenthistory-position_title': 'Rocket Scientist',
                                      'employmenthistory-organization_name': 'Blamco Inc.',
                                      'employmenthistory-start_date': '2013-01-01',
                                      'telephone-use_code':'Home',
                                      'telephone-country_dialing': 1,
                                      'telephone-area_dialing': 999,
                                      'telephone-number': 9999,
                                      'address-label': 'Home',
                                      'address-address_line_one': '123 Easy St.',
                                      'address-city_name': 'Pleasantville',
                                      'address-country_sub_division_code': 'IN',
                                      'address-country_code': 'USA',
                                      'address-postal_code': 99999,
                                      'action':'save_profile'}, follow=True)
        self.assertEquals(resp.content, 'valid')

    def test_incomplete_profile_form(self):
        # Form with incomplete sections should return a page with "This field is
        # required" errors
        resp = self.client.post(reverse('home'),
                                data={'name-given_name': 'Alice',
                                      'name-family_name': 'Smith',
                                      'name-primary':False,
                                      'education-degree_major': 'Basket Weaving',
                                      'action':'save_profile'}, follow=True)
        self.failIf(resp.context['education_form'].is_valid())
        self.assertContains(resp, 'This field is required.')
        
    def test_no_profile_duplicates(self):
        # Form with errors shouldn't save valid sections until entire form
        # is completely valid
        resp = self.client.post(reverse('home'),
                                data={'name-given_name': 'Alice',
                                      'name-family_name': 'Smith',
                                      'name-primary':False,
                                      'education-degree_major': 'Basket Weaving',
                                      'action':'save_profile'}, follow=True)
        self.assertEqual(Name.objects.count(), 0)
        self.assertEqual(Education.objects.count(), 0)
        resp = self.client.post(reverse('home'),
                                data={'name-given_name': 'Alice',
                                      'name-family_name': 'Smith',
                                      'name-primary':False,
                                      'education-organization_name': 'Stanford University',
                                      'education-degree_date': '2012-01-01',
                                      'education-education_level_code': 6,
                                      'education-degree_major': 'Basket Weaving',
                                      'action':'save_profile'}, follow=True)
        self.assertEqual(Name.objects.count(), 1)
        self.assertEqual(Education.objects.count(), 1)

    def test_delete_account(self):
        """
        Going to the delete_account view removes a user and their date completely
        """
        self.assertTrue(User.objects.all().exists())
        resp = self.client.get(reverse('delete_account'), follow=True)
        self.assertFalse(User.objects.all().exists())

    def test_disable_account(self):
        """
        Going to the disabled account view disables the account, meaning that
        (1) a new activation key is created, (2) User is set to not active and
        (3) User is set to disabled.
        """
        
        user = User.objects.get(id=self.user.id)
        custom_signals.create_activation_profile(sender=self, user=user,
                                                 email=user.email)
        profile = ActivationProfile.objects.get(user=user)
        ActivationProfile.objects.activate_user(profile.activation_key)
        profile = ActivationProfile.objects.get(user=user)
        self.assertEqual(profile.activation_key, 'ALREADY ACTIVATED')

        resp = self.client.get(reverse('disable_account'), follow=True)
        user = User.objects.get(id=self.user.id)
        profile = ActivationProfile.objects.get(user=user)
        self.assertNotEqual(profile.activation_key, 'ALREADY ACTIVATED')
        self.assertFalse(user.is_active)
        self.assertTrue(user.is_disabled)

    def test_about_template(self):
        # About page should return a status code of 200
        response = self.client.get(reverse('about'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')

    def test_batch_message_digest(self):
        """
        POSTing correct data to this view should result in new EmailLog
        instances being created.
        """
        def make_message_and_get_response(msg_time):
            message = '{{"email":"alice@example.com","timestamp":"{0}","event":"{1}"}}'
            messages = ''
            for event in self.events:
                if event != 'open':
                    # The only sources I could find suggest SendGrid uses CRLF
                    # endings.
                    messages += '\r\n'
                messages += message.format(time.mktime(msg_time.timetuple()),
                                           event)
            response = self.client.post(reverse('batch_message_digest'),
                                        data={'raw_post_data':messages})
            return response

        # Submit a batch of three events created recently
        now = datetime.datetime.now()
        response = make_message_and_get_response(now)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(EmailLog.objects.count(), 3)

        for log in EmailLog.objects.all():
            self.assertTrue(log.event in self.events)

        # Submit a batch of events created a month ago
        month_ago = now - timedelta(days=30)
        response = make_message_and_get_response(month_ago)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(EmailLog.objects.count(), 6)
        self.assertEqual(
            EmailLog.objects.filter(
                received__range=(now - timedelta(days=30), now)
            ).count(), 6
        )

        # Submit a batch of events created a month and a week ago
        month_and_week_ago = month_ago - timedelta(days=7)
        response = make_message_and_get_response(month_and_week_ago)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(EmailLog.objects.count(), 9)
        self.assertEqual(
            EmailLog.objects.filter(
                received__lte=(now - timedelta(days=37))
            ).count(), 3
        )

        response = self.client.post(reverse('batch_message_digest'),
                                    data={'raw_post_data':'this is invalid'})
        self.assertEqual(response.status_code, 500)
