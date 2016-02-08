import json

from django.test.client import RequestFactory

from mysearches.models import SavedSearch

from mysearches.views import (secure_saved_search,
                              get_value_from_request,
                              add_or_activate_saved_search,
                              user_creation_retrieval)

from mysearches.tests.factories import SavedSearchFactory


from myjobs.tests.setup import MyJobsBase
from myjobs.tests.factories import UserFactory

class SecureSavedSearchAPITestCase(MyJobsBase):
    """
    Test cases for secure saved search API (currently used by secure blocks
    saved search widget

    """

    def test_add_or_activate_function_adds_search(self):
        """
        Test to ensure the add_or_activate_saved_search function adds a search
        when provided a user and an valid URL of a search that user does not
        have

        """
        count_user_searches = SavedSearch.objects.filter(user=self.user).count()
        self.assertEqual(count_user_searches, 0,
                         msg="Expected 0 searches for user, got %s! Searches"
                             " existed before test" % count_user_searches)
        saved_search = add_or_activate_saved_search(self.user,
                                                    'http://www.my.jobs/')
        count_user_searches = SavedSearch.objects.filter(user=self.user).count()
        self.assertEqual(count_user_searches, 1,
                         msg="Expected 1 search, got %s! Search may not have"
                             "been created." % count_user_searches)

    def test_add_or_activate_function_activates_search(self):
        """
        Test to ensure the add_or_activate_saved_search function adds a search
        when provided a user and an valid URL of a search that user has and is
        inactive

        """
        new_ss = SavedSearchFactory(user=self.user, is_active=False)
        self.assertEqual(new_ss.is_active, False,
                         msg="New search was active. Factory did not set"
                             " it to inactive!")
        count_user_searches = SavedSearch.objects.filter(user=self.user).count()
        self.assertEqual(count_user_searches, 1,
                         msg="Expected 1 searches for user, got %s! Factory may"
                             " not have created search" % count_user_searches)
        saved_search = add_or_activate_saved_search(self.user,
                                                    new_ss.url)
        ss_reload = SavedSearch.objects.get()
        self.assertEqual(new_ss, ss_reload,
                         msg="There was a problem reloading saved search from"
                             "the database. Original and reload do not match!")
        self.assertEqual(ss_reload.is_active, True,
                         msg="Reloaded search was inactive! Function did not"
                             " activate it!")

    def test_add_or_activate_function_invalid_url(self):
        """
        Test to ensure the add_or_activate_saved_search function raises
        the proper exception if an invalid url is provided

        """
        count_user_searches = SavedSearch.objects.filter(user=self.user).count()
        self.assertEqual(count_user_searches, 0,
                         msg="Expected 0 searches for user, got %s! Searches"
                             " existed before test" % count_user_searches)
        with self.assertRaises(ValueError, msg="ValueError not raised despite "
                                               "invalid url provided!"):
            saved_search = add_or_activate_saved_search(self.user,
                                                        'http://www.google.com/')
        count_user_searches = SavedSearch.objects.filter(user=self.user).count()
        self.assertEqual(count_user_searches, 0,
                         msg="Expected 0 searches, got %s! Search may have"
                             " been created." % count_user_searches)

    def test_add_or_activate_function_no_url(self):
        """
        Test to ensure the add_or_activate_saved_search function raises
        proper exception if no url is provided

        """
        count_user_searches = SavedSearch.objects.filter(user=self.user).count()
        self.assertEqual(count_user_searches, 0,
                         msg="Expected 0 searches for user, got %s! Searches"
                             " existed before test" % count_user_searches)
        with self.assertRaises(ValueError, msg="ValueError not raised despite "
                                               "invalid url provided!"):
            saved_search = add_or_activate_saved_search(self.user, '')
        count_user_searches = SavedSearch.objects.filter(user=self.user).count()
        self.assertEqual(count_user_searches, 0,
                         msg="Expected 0 searches, got %s! Search may have"
                             " been created." % count_user_searches)

    def test_request_function_retrieves_post_value(self):
        """
        Test to ensure that get_value_from_request retrieves a value when
        given a key in the POST values

        """
        rf = RequestFactory()
        post_request = rf.post('/saved-search/api/secure-saved-search',
                               {'hello':'kitty'})
        kitty = get_value_from_request(post_request, 'hello')
        self.assertEqual(kitty, 'kitty', msg="Expected kitty, got %s!"
                                             "Post value was not "
                                             "retrieved." % kitty)


    def test_request_function_retrieves_get_value(self):
        """
        Test to ensure that get_value_from_request retrieves a value when
        given a key in the GET values

        """
        rf = RequestFactory()
        get_request = rf.get('/saved-search/api/secure-saved-search',
                               {'hello':'kitty'})
        kitty = get_value_from_request(get_request, 'hello')
        self.assertEqual(kitty, 'kitty', msg="Expected kitty, got %s!"
                                             "Get value was not "
                                             "retrieved." % kitty)

    def test_request_function_retrieves_body_value(self):
        """
        Test to ensure that get_value_from_request retrieves a value when
        given a key in the body values (JSON formatted)

        """
        rf = RequestFactory()
        post_data = json.dumps({'hello':'kitty'})
        post_request = rf.post('/saved-search/api/secure-saved-search',
                               post_data,
                               content_type='application/json')
        self.assertEqual(post_data, post_request.body,
                         msg="Expected %s, got %s! Post body did "
                             "not match provided data, request"
                             "was malformed!" % (post_data, post_request.body))
        kitty = get_value_from_request(post_request, 'hello')
        self.assertEqual(kitty, 'kitty', msg="Expected kitty, got %s!"
                                             "Post value was not "
                                             "retrieved." % kitty)

    def test_request_function_returns_none_if_key_doesnt_exist(self):
        """
        Test to ensure that get_value_from_request retrieves a key isn't in
        body, POST or GET

        """
        rf = RequestFactory()
        get_request = rf.get('/saved-search/api/secure-saved-search',
                               {'goodbye':'kitty'})
        kitty = get_value_from_request(get_request, 'hello')
        self.assertIsNone(kitty, msg="Expected None, got %s! A value was"
                                     "retrieved." % kitty)

    def test_return_user_if_exists_and_is_logged_in(self):
        """
        Verifies that if the email provided belongs to the authenticated user,
        that user's account is returned from user_creation_retrieval

        """
        user_account, created = user_creation_retrieval(self.user,
                                                        self.user.email)
        self.assertFalse(created)
        self.assertEqual(self.user, user_account,
                         msg="User retrieved did not match authenticated"
                             " user.")

    def test_return_user_if_email_not_taken(self):
        """
        Verifies that if an unused email is provided, a user is created for
        that user and it is returned by user_creation_retrieval

        """
        user_account, created = user_creation_retrieval(self.user,
                                                        "notsame@email.com")
        self.assertTrue(created)
        self.assertNotEqual(self.user, user_account,
                         msg="Original user was retrieved. Should have created"
                             " a new user.")

    def test_raise_error_if_email_is_already_taken(self):
        """
        Verifies that if the email provided belongs to a user that is not
        signed in, an error is raised from user_creation_retrieval

        """
        UserFactory(email="anotheruser@email.com")
        with self.assertRaises(ValueError, msg="ValueError should have raised!"
                                               " Email provided was in use."):
           user_creation_retrieval(self.user, "anotheruser@email.com")

    def test_user_retrieved_parameters_required(self):
        """
        Verifies that user_creation_retrieval only works if both auth user and
        email are provided to user_creation_retrieval

        """
        with self.assertRaises(ValueError):
            user_creation_retrieval(self.user, "",
                                    msg="Error not thrown when email empty")

        with self.assertRaises(ValueError):
            user_creation_retrieval(None, "test@email.com",
                                    msg="Error not thrown when user is none")

    def test_api_works_with_authenticated_user(self):
        """
        Verifies that the secure saved searched API works properly with
        authenticated users when a valid, unclaimed email is provided

        """
        import ipdb; ipdb.set_trace()
        request_data = {'email':self.user.email,
                        'url':'http://wwww.my.jobs/'}
        response = self.client.post('/saved-search/api/secure-saved-search',
                                    data=request_data)

    def test_api_returns_error_if_email_is_taken(self):
        """
        Verifies that the secure saved searched API returns an error if the
        provided email is taken by another user

        """

    def test_api_works_with_unauthenticated_user(self):
        """
        Verifies that the secure saved searched API works properly with
        unauthenticated users when a valid, unclaimed email is provided

        """

    def test_api_uses_authenticated_users_email_if_not_provided(self):
        """
        Verifies that the secure saved searched API works properly and uses the
        authenticated user's email address if none is provided to the API

        """

    def test_api_error_if_no_email_provided_and_user_unauthenticated(self):
        """
        Verifies that the secure saved searched API returns an error when
        an unauthenticated user does not provide an email

        """

    def test_api_requires_a_url_parameter(self):
        """
        Verifies that the secure saved searched API returns an error if a
        url is not provided.

        """