from django.core.urlresolvers import reverse
from django.conf import settings
import datetime
import pytz

from myjobs.forms import ChangePasswordForm
from myjobs.models import CompanyAccessRequest, User
from myjobs.tests.factories import UserFactory, CompanyAccessRequestFactory
from myprofile.tests.factories import PrimaryNameFactory
import hashlib
from setup import MyJobsBase


class AccountFormTests(MyJobsBase):
    def setUp(self):
        super(AccountFormTests, self).setUp()
        self.name = PrimaryNameFactory(user=self.user)

    def test_password_form(self):
        invalid_data = [
            {'data': {'password': 'cats',
                      'new_password1': '7dY=Ybtk',
                      'new_password2': '7dY=Ybtk'},
             u'errors': [['password', [u"Wrong password."]]]},
            {'data': {'password': '5UuYquA@',
                      'new_password1': '7dY=Ybtk',
                      'new_password2': 'notnewpassword'},
             u'errors': [[u'new_password2',
                         [u'The new password fields did not match.']],
                         [u'new_password1',
                         [u'The new password fields did not match.']]], },
        ]

        for item in invalid_data:
            form = ChangePasswordForm(user=self.user, data=item['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[item[u'errors'][0][0]],
                             item[u'errors'][0][1])

        form = ChangePasswordForm(user=self.user,
                                  data={'password': '5UuYquA@',
                                        'new_password1': '7dY=Ybtk',
                                        'new_password2': '7dY=Ybtk'})

        self.failUnless(form.is_valid())
        form.save()
        self.failUnless(self.user.check_password('7dY=Ybtk'))

    def test_allow_password_reuse(self):
        """
        If the company doesn't enforce password expiration, allow dup passwords
        """
        self.company.password_expiration = False
        self.company.save()
        self.user = User.objects.get(pk=self.user.pk)

        password = 'password-enTry-0293'
        self.user.set_password(password)
        self.user.save()

        form = ChangePasswordForm(
            user=self.user,
            data={
                'password': password,
                'new_password1': password,
                'new_password2': password,
            })
        self.assertTrue(form.is_valid())

    def test_prevent_password_reuse(self):
        """
        Prevent password reuse if any of the users' companies require it.
        """
        self.company.password_expiration = True
        self.company.save()
        self.user = User.objects.get(pk=self.user.pk)

        limit = settings.PASSWORD_HISTORY_ENTRIES

        def password(i):
            return 'password-enTry-%d' % i

        for i in range(0, limit + 1):
            entry = password(i)
            self.user.set_password(entry)
            self.user.save()
            last_pw = entry

        for i in range(1, limit + 1):
            entry = password(i)
            form = ChangePasswordForm(
                user=self.user,
                data={
                    'password': last_pw,
                    'new_password1': entry,
                    'new_password2': entry,
                })
            self.assertFalse(form.is_valid())
            self.assertRegexpMatches(
                form.errors['new_password1'][0],
                r'different from the previous')

        entry = password(0)
        form = ChangePasswordForm(
            user=self.user,
            data={
                'password': last_pw,
                'new_password1': entry,
                'new_password2': entry,
            })
        self.assertTrue(form.is_valid())


class CompanyAccessRequestFormTests(MyJobsBase):
    def test_approval_form_authenticates_request(self):
        """
        Submitting a valid authentication code should result in the request
        being updated and a new admin being assigned.
        """

        # required for django admin during tests, apparently
        self.user.is_superuser = True
        self.user.save()

        # give us a handle to the unhashed access code
        access_code = '1234ABCD'
        requesting_user = UserFactory(email="requestuser@example.com")
        request = CompanyAccessRequestFactory(
            access_code=hashlib.md5(access_code).hexdigest(),
            requested_by=requesting_user)

        # code shouldn't have been authorized yet
        self.assertFalse(request.authorized_by)

        data = {
            "company": self.company.pk,
            "verification_code": access_code
        }
        admin_url = "%s%s/" % (
            reverse("admin:myjobs_companyaccessrequest_changelist"),
            request.pk)
        self.client.post(path=admin_url, data=data)

        # object is cached so we need to refetch it
        access_request = CompanyAccessRequest.objects.get(pk=request.pk)
        self.assertEqual(access_request.authorized_by, self.user)

    def test_expired_request(self):
        """
        Expired requests should not be authenticated.

        """
        # required for django admin during tests, apparently
        self.user.is_superuser = True
        self.user.save()

        # give us a handle to the unhashed access code
        access_code = '1234ABCD'
        requesting_user = UserFactory(email="requestuser@example.com")
        yesterday = datetime.datetime.now(
            tz=pytz.UTC) - datetime.timedelta(days=1)
        request = CompanyAccessRequestFactory(
            access_code=hashlib.md5(access_code).hexdigest(),
            requested_by=requesting_user)

        # force the request to be expired
        request.requested_on = yesterday
        request.save()

        self.assertTrue(request.expired)

        data = {
            "company": self.company.pk,
            "verification_code": access_code
        }
        admin_url = reverse("admin:myjobs_companyaccessrequest_change",
                            args=(request.pk,))
        response = self.client.post(path=admin_url, data=data, follow=True)

        # object is cached so we need to refetch it
        access_request = CompanyAccessRequest.objects.get(pk=request.pk)
        self.assertEqual(access_request.authorized_by, None)
