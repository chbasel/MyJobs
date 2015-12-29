import datetime

from django.contrib.sessions.models import Session
from django.core.urlresolvers import reverse

from setup import MyJobsBase
from myjobs.tests.factories import UserFactory
from myjobs.tests.test_views import TestClient


class MyJobsHelpersTests(MyJobsBase):
    def setUp(self):
        super(MyJobsHelpersTests, self).setUp()
        self.user = UserFactory()
        self.client = TestClient()

        self.login_params = {'username': 'alice@example.com',
                             'password': '5UuYquA@',
                             'action': 'login'}

    def test_login_dont_remember_me(self):
        self.assertEqual(Session.objects.count(), 0)
        self.assertEqual(Session.objects.count(), 1)

        session = Session.objects.all()[0]

        session_dict = session.get_decoded()
        user_id = session_dict['_auth_user_id']
        self.assertEqual(user_id, self.user.id)

        # session.expire_date is tz aware; datetime.datetime.now is naive
        # It probably isn't worth it to bring in pytz just for tests
        now = datetime.datetime.now(session.expire_date.tzinfo)
        diff = session.expire_date - now

        # Due to the delay between the post at the top of this test
        # and reaching this line, this can't be an assertEquals;
        self.assertTrue(880 <= diff.total_seconds() <= 900)

    def test_login_remember_me(self):
        self.assertEqual(Session.objects.count(), 0)
        self.login_params['remember_me'] = True
        response = self.client.post(reverse('home'),
                                    data=self.login_params)
        self.assertEqual(Session.objects.count(), 1)

        session = Session.objects.all()[0]

        session_dict = session.get_decoded()
        user_id = session_dict['_auth_user_id']
        self.assertEqual(user_id, self.user.id)

        weeks = (datetime.datetime.now() + datetime.timedelta(days=14))
        # Session expiration should be two weeks from now - comparing number
        # of days should be good enough
        self.assertEqual(session.expire_date.toordinal(), weeks.toordinal())
