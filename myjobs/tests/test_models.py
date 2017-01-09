import datetime
import pytz
import urllib
from django.test import TestCase
from django.contrib.auth.models import Group
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q
from django.http import Http404
from django.utils.http import urlquote
from django.utils import timezone

import pytz

from setup import MyJobsBase
from myjobs.models import User, Role, SecondPartyAccessRequest
from myjobs.tests.test_views import TestClient
from myjobs.tests.factories import (UserFactory, AppAccessFactory,
                                    ActivityFactory, RoleFactory,
                                    CompanyAccessRequestFactory)
from mymessages.models import Message
from myprofile.models import SecondaryEmail, Name, Telephone
from mysearches.models import PartnerSavedSearch
from mysearches.tests.factories import PartnerSavedSearchFactory
from myreports.models import Report
from seo.models import SeoSite
from seo.tests.factories import CompanyFactory


class UserManagerTests(MyJobsBase):
    user_info = {'password1': 'complicated_password',
                 'email': 'alice1@example.com',
                 'send_email': True}

    def test_user_validation(self):
        user_info = {'password1': 'complicated_password',
                     'email': 'Bad Email'}
        with self.assertRaises(ValidationError):
            User.objects.create_user(**user_info)
        self.assertEqual(User.objects.count(), 1)

    def test_user_creation(self):
        new_user, _ = User.objects.create_user(**self.user_info)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(new_user.is_active, True)
        self.assertEqual(new_user.is_verified, False)
        self.assertEqual(new_user.email, 'alice1@example.com')
        self.failUnless(new_user.check_password('complicated_password'))
        self.failUnless(new_user.groups.filter(name='Job Seeker').count() == 1)
        self.assertIsNotNone(new_user.user_guid)

    def test_superuser_creation(self):
        new_user = User.objects.create_superuser(
            **{'password': 'complicated_password',
               'email': 'alice1@example.com'})
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(new_user.is_superuser, True)
        self.assertEqual(new_user.is_staff, True)
        self.assertEqual(new_user.email, 'alice1@example.com')
        self.failUnless(new_user.check_password('complicated_password'))
        self.failUnless(new_user.groups.filter(name='Job Seeker').count() == 1)
        self.assertIsNotNone(new_user.user_guid)

    def test_gravatar_url(self):
        """
        Test that email is hashed correctly and returns a 200 response
        """
        user = UserFactory(email="alice1@example.com")
        gravatar_url = "http://www.gravatar.com/avatar/c160f8cc69a4f0b" \
                       "f2b0362752353d060?s=20&d=mm"
        no_gravatar_url = ("<div class='gravatar-blank gravatar-danger' "
                           "style='height: 20px; width: 20px'>"
                           "<span class='gravatar-text' "
                           "style='font-size:13.0px;'>A</span></div>")
        generated_gravatar_url = user.get_gravatar_url()
        self.assertEqual(no_gravatar_url, generated_gravatar_url)
        status_code = urllib.urlopen(gravatar_url).getcode()
        self.assertEqual(status_code, 200)

    def test_not_disabled(self):
        """
        An anonymous user who provides the :verify: query string or
        user with is_disabled set to True should be redirected to the home
        page. An anonymous user who does not should see a 404. A user with
        is_active set to False should proceed to their destination.
        """
        client = TestClient()
        user = UserFactory(email="alice1@example.com")

        # Anonymous user
        resp = client.get(reverse('view_profile'))
        path = resp.request.get('PATH_INFO')
        self.assertRedirects(resp, reverse('home') + '?next=' + path)

        # This is ugly, but it is an artifact of the way Django redirects
        # users who fail the `user_passes_test` decorator.
        qs = '?verify=%s' % user.user_guid
        next_qs = '?next=' + urlquote('/profile/view/%s' % qs)

        # Anonymous user navigates to url with :verify: in query string
        resp = client.get(reverse('view_profile') + qs)
        # Old path + qs is urlquoted and added to the url as the :next: param
        self.assertRedirects(resp, "http://testserver/" + next_qs)

        # Active user
        client.login_user(user)
        resp = client.get(reverse('view_profile'))
        self.assertTrue(resp.status_code, 200)

        # Disabled user
        user.is_disabled = True
        user.save()
        resp = client.get(reverse('view_profile'))
        self.assertRedirects(resp, "http://testserver/?next=/profile/view/")

    def test_inactive_user_sees_message(self):
        """
        A user with is_verified or is_active set to False should see an
        activation message instead of the content they were originally meaning
        to see.
        """
        client = TestClient(path=reverse('saved_search_main'))
        user = UserFactory(email="alice1@example.com")

        # Active user
        client.login_user(user)
        resp = client.get()
        self.assertIn('Saved Search', resp.content)

        # Inactive user
        user.is_verified = False
        user.save()
        resp = client.get()
        self.assertIn('unavailable', resp.content)

    def test_group_status(self):
        """
        Should return True if user is assigned a role for at least one company.
        This method will hopefully be deprecated soon.

        """
        user = UserFactory(email="alice1@example.com")
        self.assertFalse(User.objects.is_group_member(user, "dummy"))
        user.roles.add(self.role)
        self.assertTrue(User.objects.is_group_member(user, "dummy"))


    def test_user_with_multiple_profileunits(self):
        """
        Confirms that the owner of an email is correctly being found.

        """
        user, _ = User.objects.create_user(**self.user_info)
        SecondaryEmail.objects.create(user=user, email='secondary@email.test')
        Telephone.objects.create(user=user)
        Name.objects.create(user=user, given_name="Test", family_name="Name")
        owner_user = User.objects.get_email_owner(user.email)
        self.assertEqual(owner_user.pk, user.pk)
        owner_user = User.objects.get_email_owner('secondary@email.test')
        self.assertEqual(owner_user.pk, user.pk)

    def test_deleting_user_does_not_cascade(self):
        """
        Deleting a user shouldn't delete related objects such as partner saved
        searches and reports.
        """

        user = UserFactory(email="alice1@example.com")
        company = CompanyFactory()
        pss = PartnerSavedSearchFactory(user=self.user, created_by=user)
        report = Report.objects.create(created_by=user, owner=company)

        user.delete()
        self.assertIn(pss, PartnerSavedSearch.objects.all())
        self.assertIn(report, Report.objects.all())


class TestPasswordExpiration(TestCase):
    """Test password expiration"""

    def setUp(self):
        super(TestPasswordExpiration, self).setUp()

        (self.user, _) = User.objects.create_user(
            password='somepass',
            email='someuser@example.com')
        self.strict = CompanyFactory(password_expiration=True, name='strict')
        self.strict_role = RoleFactory(company=self.strict, name="Admin")
        self.loose = CompanyFactory(password_expiration=False, name='loose')
        self.loose_role = RoleFactory(company=self.loose, name="Admin")
        self.user.roles.add(self.strict_role)
        self.user.roles.add(self.loose_role)

        # Reload from db to get correct password state.
        self.user = User.objects.get(pk=self.user.pk)

    def test_no_company(self):
        """Users with no company should not have password expiration"""
        self.user.roles.clear()
        self.assertEqual(
            False,
            self.user.has_password_expiration())
        self.assertEqual(
            False,
            self.user.is_password_expired())

        self.user.password = 'somepass2'
        self.user.save()
        self.assertEqual(None, self.user.password_last_modified)
        self.assertEqual(0, self.user.userpasswordhistory_set.count())

    def test_use_loose_companies_only(self):
        """Making the strict company loose should disable expiration."""
        self.strict.password_expiration = False
        self.strict.save()
        self.assertEqual(False, self.user.has_password_expiration())

    def test_use_stricter_company(self):
        """Users with any strict company should have password expiration"""
        self.assertEqual(True, self.user.has_password_expiration())

    def test_first_expirable_login(self):
        """is_password_expired is True when the user has never logged in."""
        self.assertEqual(True, self.user.is_password_expired())

    def test_login_within_expire_window(self):
        """is_password_expired is False when in the expiration window."""
        self.user.password_last_modified = (
            timezone.now() - datetime.timedelta(days=1))
        self.user.save()
        self.assertEqual(False, self.user.is_password_expired())

    def test_login_out_of_expire_window(self):
        """is_password_expired is True when past the expiration window."""
        days = settings.PASSWORD_EXPIRATION_DAYS
        self.user.password_last_modified = (
            timezone.now() - datetime.timedelta(days))
        self.user.save()
        self.assertEqual(True, self.user.is_password_expired())

    def test_change_password(self):
        """
        Changing password for a user in a company does sets pasword last
        modified time.
        """
        before_password_set = timezone.now()
        self.user.set_password('somepass2')
        self.user.save()
        self.assertGreater(
            self.user.password_last_modified, before_password_set)
        self.assertEqual(1, self.user.userpasswordhistory_set.count())

    def test_history_limit(self):
        """
        Adding to the password history should exceed the history limit.
        """
        limit = settings.PASSWORD_HISTORY_ENTRIES
        for i in range(0, limit + 2):
            date = (
                datetime.datetime(2016, 1, 1, tzinfo=pytz.UTC) +
                datetime.timedelta(days=i))
            self.user.add_password_to_history('entry-%d' % i, date)
            self.assertLess(0, self.user.userpasswordhistory_set.count())
            self.assertLessEqual(
                self.user.userpasswordhistory_set.count(),
                limit)
        hashes = set(
            h.password_hash
            for h in self.user.userpasswordhistory_set.all())
        self.assertNotIn('entry-0', hashes)
        self.assertEquals(limit, len(hashes))

    def test_is_password_in_history(self):
        """
        Don't let the user reuse a password they used recently.
        """
        limit = settings.PASSWORD_HISTORY_ENTRIES
        for i in range(0, limit + 1):
            self.user.set_password('entry-%d' % i)
            self.user.save()
        self.assertFalse(self.user.is_password_in_history('entry-0'))
        for i in range(1, limit + 1):
            entry = 'entry-%d' % i
            self.assertTrue(self.user.is_password_in_history(entry), entry)

    def test_is_password_in_history_disabled(self):
        """
        Disable history checking if password expiration is off.
        """
        limit = settings.PASSWORD_HISTORY_ENTRIES
        for i in range(0, limit):
            self.user.set_password('entry-%d' % i)
            self.user.save()
        self.strict.password_expiration = False
        self.strict.save()
        for i in range(0, limit):
            entry = 'entry-%d' % i
            self.assertFalse(self.user.is_password_in_history(entry), entry)

    def test_lockout_counter(self):
        """
        Keep track of failed login attempts.
        """
        limit = settings.PASSWORD_ATTEMPT_LOCKOUT
        for i in range(0, limit):
            self.assertFalse(self.user.is_locked_out(), 'iteration %d' % i)
            self.user.note_failed_login()
        self.assertTrue(self.user.is_locked_out())
        self.user.reset_lockout()
        self.assertFalse(self.user.is_locked_out())


class TestActivities(MyJobsBase):
    """Tests the relationships between activities, roles, and app access."""

    def test_role_unique_to_company(self):
        """Roles should be unique to company by name."""

        try:
            # This should be allowed since the company is different
            RoleFactory(name=self.role.name)
        except IntegrityError:
            self.fail("Creating a similar role for a different company should "
                      "be allowed, but it isn't.")

        # we shouldn't be allowed to create a role wit the same name in the
        # same company
        with self.assertRaises(IntegrityError):
            RoleFactory(name=self.role.name, company=self.role.company)

    def test_activity_names_unique(self):
        """Activities should have unique names."""

        activity = self.activities[0]
        with self.assertRaises(IntegrityError):
            ActivityFactory(name=activity.name)

    def test_app_access_names_unique(self):
        """App access levels should have unique names."""

        with self.assertRaises(IntegrityError):
            AppAccessFactory(name=self.app_access.name)

    def test_automatic_role_admin_activities(self):
        """
        New activities should be added to all Admin roles automatically.

        """
        activities = ActivityFactory.create_batch(5)
        self.role.activities = activities
        self.role.name = "Test Role"
        self.role.save()
        # sanity check for initial numbers
        for admin in Role.objects.filter(name="Admin"):
            self.assertEqual(admin.activities.count(), 5)

        new_activity = ActivityFactory(
            name="new activity", description="Just a new test activity.")

        # new activity should be available for admins
        for admin in Role.objects.filter(name="Admin"):
            self.assertIn(new_activity, admin.activities.all())

        # existing role should not have new activity
        self.assertNotIn(new_activity, self.role.activities.all())

    def test_can_method_with_app_access(self):
        """
        ``User.can`` should return False when a user isn't associated with the
        correct activities and True when they are.
        """

        user = UserFactory(email="alice1@example.com", roles=[self.role])
        self.role.activities = self.activities
        activities = self.role.activities.values_list('name', flat=True)

        # check for a single activity
        self.assertTrue(user.can(self.company, activities[0]))

        self.assertFalse(user.can(self.company, "eat a burrito"))

        # check for multiple activities
        self.assertTrue(user.can(self.company, *activities))

        self.assertFalse(user.can(
            self.company, activities[0], "eat a burrito"))

    def test_can_method_without_app_access(self):
        """
        ``User.can`` should raise an Http404 when the company doesn't have
        sufficient app-level access.

        """
        self.role.activities = self.activities
        activities = self.role.activities.values_list('name', flat=True)
        self.user.roles = [self.role]
        self.company.app_access.clear()

        with self.assertRaises(Http404):
            self.user.can(self.company, activities[0])

    def test_send_invite_method(self):
        """
        `User.send_invite called without a role should send an invitation
        email, optionally assiging the reserved user to a role if one was
        passed in.
        """
        self.role.activities = self.activities

        # sanity check
        self.assertTrue(self.user.can(self.company, 'create user'))

        user = self.user.send_invite(
            'regular@joe.com', self.company, role_name=self.role.name)
        self.assertTrue(
            user.can(self.company, 'create user'),
            "User should be able to 'create user' but can't.")

    def test_activities(self):
        """
        `User.get_activities(company)` should return a list of activities
        associated with this user and company.

        """
        user = UserFactory(email="alice1@example.com")

        self.assertItemsEqual(user.get_activities(self.company), [])

        user.roles.add(self.role)
        activities = self.role.activities.values_list('name', flat=True)

        self.assertItemsEqual(user.get_activities(self.company), activities)

    def test_access_code_expiration(self):
        """Any access code older than 1 day should be considered expired."""

        now = datetime.datetime.now(tz=pytz.UTC)
        yesterday = now - datetime.timedelta(days=1)

        access_request = CompanyAccessRequestFactory(
            requested_by=self.user, requested_on=now)

        self.assertFalse(access_request.expired)

        access_request.requested_on = yesterday
        access_request.save()

        self.assertTrue(access_request.expired)


class RemoteAccessRequestModelTests(MyJobsBase):
    def setUp(self):
        super(RemoteAccessRequestModelTests, self).setUp()
        self.password = '5UuYquA@'
        self.client = TestClient()
        self.client.login(email=self.user.email, password=self.password)

        self.account_owner = UserFactory(email='accounts@my.jobs',
                                         password=self.password)
        self.impersonate_url = reverse('impersonate-start', kwargs={
            'uid': self.account_owner.pk})
        self.site = SeoSite.objects.first()

    def test_create_request_sends_messages(self):
        """
        The requesting of remote access should send both a My.jobs message
        and an email to the account owner.
        """
        msg = "User had %s messages, expected %s"
        mail.outbox = []
        spar = SecondPartyAccessRequest.objects.create(
            account_owner=self.account_owner, second_party=self.user,
            site=self.site, reason='just cuz')
        self.assertEqual(len(mail.outbox), 1)

        # We're logged in as the requesting user at this point and should
        # not have any messages.
        response = self.client.get(reverse('home'))
        self.assertEqual(len(response.context['new_messages']), 0,
                         msg=msg % (len(response.context['new_messages']), 0))

        response = self.client.get(reverse('impersonate-approve',
                                           kwargs={'access_id': spar.id}))
        self.assertEqual(response.status_code, 403,
                         msg=("Unauthorized approval of a request should not "
                              "happen but did"))

        # Log out then log in as the account owner.
        self.client.get(reverse('auth_logout'))
        self.client.login(email=self.account_owner.email,
                          password=self.password)
        response = self.client.get(reverse('home'))

        # We should now have one My.jobs message.
        messages = response.context['new_messages']
        self.assertEqual(len(messages), 1,
                         msg=msg % (len(response.context['new_messages']), 1))
        message = messages[0]
        email = mail.outbox[0]
        self.assertEqual(message.message.body, email.body,
                         msg="Message and email bodies were not identical")
        for text in ['>Allow<', '>Deny<', spar.reason,
                     self.user.get_full_name(default=self.user.email)]:
            self.assertTrue(text in email.body,
                            msg="%s not in email body" % text)
        response = self.client.get(reverse('impersonate-approve',
                                           kwargs={'access_id': spar.id}))
        spar = SecondPartyAccessRequest.objects.get(pk=spar.pk)
        self.assertEqual(spar.accepted, True,
                         msg="Acceptance status was not updated")
