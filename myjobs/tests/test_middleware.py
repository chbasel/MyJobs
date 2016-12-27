from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test.client import RequestFactory

from setup import MyJobsBase
from middleware import PasswordChangeRedirectMiddleware, SessionTimeMiddleware


class RedirectMiddlewareTests(MyJobsBase):
    def setUp(self):
        super(RedirectMiddlewareTests, self).setUp()
        self.redirect_middleware = PasswordChangeRedirectMiddleware()
        self.request_factory = RequestFactory()

    def test_logged_in_no_redirect(self):
        """
        A logged in user whose password_change flag is not set
        should proceed to their original destination
        """
        request = self.request_factory.get(reverse('edit_account'))
        request.user = self.user
        response = self.redirect_middleware.process_request(request)
        self.assertEqual(response, None)

    def test_logged_in_autocreated_user_redirects(self):
        """
        A logged in user whose password_change flag is set should
        be redirected to the password change form
        """
        self.user.password_change = True
        self.user.save()

        request = self.request_factory.get(reverse('saved_search_main'))
        request.user = self.user

        response = self.redirect_middleware.process_request(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get('location'),
                         reverse('edit_account')+"#as-password")

    def test_not_logged_in_returns_forbidden(self):
        """
        An anonymous user that tries to post to a private url should
        receive a 403 Forbidden status
        """
        request = self.request_factory.get(reverse('saved_search_main'),
                                           HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        new_request = request.GET.copy()
        new_request['next'] = reverse('home')
        request.GET = new_request
        request.REQUEST.dicts = (new_request, request.POST)
        request.user = AnonymousUser()
        response = self.redirect_middleware.process_request(request)
        self.assertEqual(response.status_code, 403)


class SessionTimeMiddlewareTest(MyJobsBase):
    def setUp(self):
        super(SessionTimeMiddlewareTest, self).setUp()
        self.middleware = SessionTimeMiddleware()
        self.request_factory = RequestFactory()
        self.response = HttpResponse()

    def test_logged_in_proper_exp_cookie(self):
        """
        A logged in user should get a cookie 'exp' that expires at the
        same time as the session.

        """

        request = self.request_factory.get(reverse('edit_account'))
        request.user = self.user
        request.session = self.client.session
        response = self.middleware.process_response(request, self.response)

        self.assertTrue('exp' in response.cookies)
        self.assertEqual(response.cookies['exp']['expires'],
                         self.client.session.get_expiry_age())

    def test_not_logged_in_no_exp_cookie(self):
        """
        When there is no logged in user the exp cookie should never get set.

        """
        request = self.request_factory.get(reverse('edit_account'))
        response = self.middleware.process_response(request, self.response)

        self.assertFalse('exp' in response.cookies)
