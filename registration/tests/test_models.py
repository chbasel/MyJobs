import datetime
import hashlib
import re

from bs4 import BeautifulSoup

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from myjobs.models import User
from myjobs.tests.factories import UserFactory
from myjobs.tests.setup import MyJobsBase
from myprofile.tests.factories import PrimaryNameFactory
from registration.models import ActivationProfile, Invitation
from registration.tests.factories import InvitationFactory
from seo.tests.factories import CompanyFactory


class RegistrationModelTests(MyJobsBase):
    """
    Test the model and manager used in the default backend.

    """
    user_info = {'password1': 'swordfish',
                 'email': 'alice@example.com',
                 'send_email': True}

    def setUp(self):
        super(RegistrationModelTests, self).setUp()
        self.user.delete()
        self.old_activation = getattr(settings, 'ACCOUNT_ACTIVATION_DAYS', None)
        settings.ACCOUNT_ACTIVATION_DAYS = 7

    def tearDown(self):
        super(RegistrationModelTests, self).tearDown()
        settings.ACCOUNT_ACTIVATION_DAYS = self.old_activation

    def test_profile_creation(self):
        """
        Creating a registration profile for a user populates the
        profile with the correct user and a SHA1 hash to use as
        activation key.

        """
        new_user, created = User.objects.create_user(**self.user_info)
        profile = ActivationProfile.objects.get(user=new_user)
        self.assertEqual(ActivationProfile.objects.count(), 1)
        self.assertEqual(profile.user.id, new_user.id)
        self.failUnless(re.match('^[a-f0-9]{40}$', profile.activation_key))
        self.assertEqual(unicode(profile),
                         "Registration for alice@example.com")

    def test_user_creation_email(self):
        """
        By default, creating a new user sends an activation email.

        """
        User.objects.create_user(**self.user_info)
        self.assertEqual(len(mail.outbox), 1)

    def test_user_creation_no_email(self):
        """
        Passing ``send_email=False`` when creating a new user will not
        send an activation email.

        """
        self.user_info['send_email'] = False
        User.objects.create_user(
            site=Site.objects.get_current(),
            **self.user_info)
        self.assertEqual(len(mail.outbox), 0)

    def test_unexpired_account(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``False``
        within the activation window.

        """
        new_user, _ = User.objects.create_user(**self.user_info)
        profile = ActivationProfile.objects.get(user=new_user)
        self.failIf(profile.activation_key_expired())

    def test_expired_account(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``True``
        outside the activation window.

        """
        new_user, created = User.objects.create_user(**self.user_info)
        profile = ActivationProfile.objects.get(user=new_user)
        profile.sent -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        profile.save()
        self.failUnless(profile.activation_key_expired())

    def test_valid_activation(self):
        """
        Activating a user within the permitted window makes the
        account active, and resets the activation key.

        """
        new_user, created = User.objects.create_user(**self.user_info)
        profile = ActivationProfile.objects.get(user=new_user)
        activated = ActivationProfile.objects.activate_user(profile.activation_key)

        self.failUnless(isinstance(activated, User))
        self.assertEqual(activated.id, new_user.id)
        self.failUnless(activated.is_active)
        self.failUnless(activated.is_verified)

        profile = ActivationProfile.objects.get(user=new_user)
        self.assertEqual(profile.activation_key, ActivationProfile.ACTIVATED)

    def test_expired_activation(self):
        """
        Attempting to activate outside the permitted window does not
        activate the account.

        """
        new_user, created = User.objects.create_user(**self.user_info)

        profile = ActivationProfile.objects.get(user=new_user)
        profile.sent -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        profile.save()
        activated = ActivationProfile.objects.activate_user(profile.activation_key)

        self.failIf(isinstance(activated, User))
        self.failIf(activated)

        new_user = User.objects.get(email='alice@example.com')
        self.failIf(new_user.is_verified)

        profile = ActivationProfile.objects.get(user=new_user)
        self.assertNotEqual(profile.activation_key, ActivationProfile.ACTIVATED)

    def test_activation_invalid_key(self):
        """
        Attempting to activate with a key which is not a SHA1 hash
        fails.

        """
        self.failIf(ActivationProfile.objects.activate_user('foo'))

    def test_activation_already_activated(self):
        """
        Attempting to re-activate an already-activated account fails.

        """
        new_user, created = User.objects.create_user(**self.user_info)
        profile = ActivationProfile.objects.get(user=new_user)
        ActivationProfile.objects.activate_user(profile.activation_key)

        profile = ActivationProfile.objects.get(user=new_user)
        self.failIf(ActivationProfile.objects.activate_user(profile.activation_key))

    def test_manually_send_activation(self):
        """
        Atttempting to send an activation email outside of a view shouldn't
        result in an exception.

        """
        # when running in console, settings.SITE isn't set
        del settings.SITE

        user = UserFactory(email='activation@test.com')
        activation = ActivationProfile(user=user)
        activation.send_activation_email()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('activated', mail.outbox[0].body)

    def test_activation_nonexistent_key(self):
        """
        Attempting to activate with a non-existent key (i.e., one not
        associated with any account) fails.

        """
        # Due to the way activation keys are constructed during
        # registration, this will never be a valid key.
        invalid_key = hashlib.sha1('foo').hexdigest()
        self.failIf(ActivationProfile.objects.activate_user(invalid_key))

    def test_expired_user_deletion(self):
        """
        ``RegistrationProfile.objects.delete_expired_users()`` only
        deletes inactive users whose activation window has expired.

        """
        User.objects.create_user(**self.user_info)
        expired_user, created = User.objects.create_user(
            password1='5UuYquA@', email='bob@example.com')

        profile = ActivationProfile.objects.get(user=expired_user)
        profile.sent -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        profile.save()

        ActivationProfile.objects.delete_expired_users()
        self.assertEqual(ActivationProfile.objects.count(), 1)
        self.assertRaises(User.DoesNotExist, User.objects.get, email='bob@example.com')

    def test_reset_activation(self):
        """
        Calling the reset_activation method on the ActivationProfile model
        generates a new activation key, even if it was already activated.
        """

        new_user, created = User.objects.create_user(**self.user_info)
        profile = ActivationProfile.objects.get(user=new_user)
        ActivationProfile.objects.activate_user(profile.activation_key)
        profile = ActivationProfile.objects.get(user=new_user)
        self.assertEqual(profile.activation_key, 'ALREADY ACTIVATED')
        profile.reset_activation()
        self.assertNotEqual(profile.activation_key, 'ALREADY ACTIVATED')

    def test_reactivate_disabled_user(self):
        for time in [datetime.timedelta(days=0),
                     datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)]:
            new_user, created = User.objects.create_user(**self.user_info)
            new_user.date_joined -= time
            new_user.disable()
            profile = ActivationProfile.objects.get(user=new_user)

            activated = ActivationProfile.objects.activate_user(profile.activation_key)

            self.failUnless(isinstance(activated, User))
            self.assertEqual(activated.id, new_user.id)
            self.failUnless(activated.is_active)

            profile = ActivationProfile.objects.get(user=new_user)
            self.assertEqual(profile.activation_key, ActivationProfile.ACTIVATED)


class InvitationModelTests(MyJobsBase):
    def setUp(self):
        super(InvitationModelTests, self).setUp()
        self.user.is_superuser = True
        self.user.save()

    def test_invitation_model_save_success(self):
        self.assertEqual(User.objects.count(), 1)
        for args in [{'invitee_email': self.user.email},
                     {'invitee': self.user},
                     {'invitee_email': 'new_user@example.com'}]:
            args.update({'inviting_user': self.user})
            invitation = Invitation.objects.create(**args)
            invitation.send()
        self.assertEqual(User.objects.count(), 2)

    def test_invitation_model_save_failure(self):
        """
        When we try to create an invitation with no invitee or we provide a
        mismatched User instance and email address, we should raise an
        exception
        """
        for args, exception_text in [({'invitee_email': 'new_user@example.com',
                                       'invitee': self.user},
                                      'Invitee information does not match'),
                                     ({}, 'Invitee not provided')]:
            with self.assertRaises(ValidationError) as e:
                invitation = Invitation.objects.create(**args)
            self.assertEqual(e.exception.messages, [exception_text])

    def admin_invitation(self, user, company):
        """
        Creates an Admin user  and ensures that the email generated contains
        the information that an invitation should contain.

        Returns the body of the email as parsed by BeautifulSoup for further
        review in the calling test.
        """
        self.role.name = "Admin"
        self.role.save()
        self.user.roles.add(self.role)
        company.role_set.add(self.role)

        self.assertEqual(len(mail.outbox), 0)
        self.user.send_invite(user.email, company, "Admin")
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox.pop()
        self.assertTrue('invitation' in email.subject)
        self.assertEqual(email.from_email, 'accounts@my.jobs')
        self.assertTrue(self.user.email in email.body)
        self.assertTrue(company.name in email.body)

        body = BeautifulSoup(email.body)

        self.assertTrue(
            body.select('a[href$="%s"]' % reverse('home')))

        return body

    def test_invitation_emails_verified_user(self):
        """
        Invitations to verified users don't contain activation links. It should
        be sufficient to rely on the assertions that admin_invitation
        makes and then assert that the only anchor in the email body is a
        login link.
        """
        company = CompanyFactory()
        user = UserFactory(email='companyuser@company.com',
                           is_verified=True)

        body = self.admin_invitation(user, company)

        self.assertTrue(body.select('a'))

    def test_invitation_emails_unverified_user(self):
        """
        Invitations to unverified users should contain activation links, in
        addition to the information that admin_invitation tests for.
        """
        company = CompanyFactory()
        user = UserFactory(email='companyuser@company.com',
                           is_verified=False)

        body = self.admin_invitation(user, company)

        ap = ActivationProfile.objects.get(email=user.email)

        # There should be two anchors present, one of which was tested for in

        # admin_invitation...
        self.assertEqual(len(body.select('a')), 2)
        # ...and the remaining anchor should be an activation link.
        expected_activation_href = 'https://secure.my.jobs%s?verify=%s' % (
            reverse('invitation_activate', args=[ap.activation_key]),
            user.user_guid)
        self.assertTrue(body.select('a[href="%s"]' % expected_activation_href))

        self.client.logout()
        # Test the activation link from the email.
        self.client.get(expected_activation_href)

        # If it was a valid link, the current user should now be verified.
        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.is_verified)

    def test_invitation_emails_new_user(self):
        self.assertEqual(len(mail.outbox), 0)
        invitation = Invitation.objects.create(
            invitee_email='prm_user@company.com',
            inviting_user=self.user)
        invitation.send()
        self.assertEqual(len(mail.outbox), 1)

        user = User.objects.get(email='prm_user@company.com')
        self.assertTrue(user.in_reserve)
        self.assertFalse(user.is_verified)
        email = mail.outbox.pop()
        self.assertTrue('invitation' in email.subject)
        self.assertEqual(email.from_email, 'accounts@my.jobs')
        self.assertTrue(self.user.email in email.body)

        ap = ActivationProfile.objects.get(email=user.email)

        body = BeautifulSoup(email.body)
        activation_anchor = body.select('a[href*="%s"]' % reverse(
                'invitation_activate', args=[ap.activation_key]))
        self.assertTrue(activation_anchor)
        activation_href = activation_anchor[0].attrs['href'].replace(
            'https://secure.my.jobs', '')

        self.client.logout()
        response = self.client.get(activation_href)
        self.assertTrue('Your temporary password is ' in response.content)

        user = User.objects.get(pk=user.pk)
        self.assertFalse(user.in_reserve)
        self.assertTrue(user.is_verified)

    def test_invitation_email_with_name(self):
        PrimaryNameFactory(user=self.user)

        invitation = Invitation.objects.create(
            invitee_email='prm_user@company.com', inviting_user=self.user)
        invitation.send()

        email = mail.outbox.pop()
        self.assertTrue(self.user.get_full_name() in email.body)
