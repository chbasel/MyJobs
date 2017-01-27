import json

from django.core import mail
from django.core.urlresolvers import reverse

from myjobs.tests.factories import RoleFactory, UserFactory
from myjobs.models import AppAccess
from seo.tests.factories import CompanyFactory
from setup import MyJobsBase


class ManageUsersTests(MyJobsBase):
    """
    Tests the manage users APIs, which is used to CRUD roles and users.
    """

    def setUp(self):
        super(ManageUsersTests, self).setUp()
        self.role.activities = self.activities
        self.otherCompany = CompanyFactory(app_access=[self.app_access])
        self.otherRole = RoleFactory(company=self.company, name="OtherRole")
        self.otherRoleAtOtherCompany = RoleFactory(
            company=self.otherCompany, name="otherRoleAtOtherCompany")
        self.user.roles.add(self.otherRole, self.otherRoleAtOtherCompany)

    def test_activities(self):
        """
        Tests that the Activities API returns the proper data in the
        proper form.

        """
        response = self.client.get(reverse('api_get_activities'))
        results = json.loads(response.content)

        # ensure we have a key for each app level access
        apps = list(AppAccess.objects.values_list('name', flat=True))
        self.assertEqual(apps, results.keys())

        # ensure that activities are of the correct shape
        activity = results[apps[0]][0]
        expected_shape = {'id': int, 'name': unicode, 'description': unicode,
                          'display_text': unicode}
        actual_shape = {key: type(value) for key, value in activity.items()}
        self.assertEqual(expected_shape, actual_shape)

    def test_create_role_require_post(self):
        """
        Tests creating a role
        Requires POST
        """
        response = self.client.get(reverse('api_create_role'))
        output = json.loads(response.content)
        self.assertEqual(output["success"], "false")
        self.assertEqual(output["message"], "POST method required.")

    def test_create_role_unique_role(self):
        """
        Tests creating a role
        Roles must have a unique name per company
        """
        expected_role_name = self.role.name

        response = self.client.post(reverse('api_create_role'),
                                    data={'role_name': expected_role_name})
        output = json.loads(response.content)
        self.assertEqual(output["success"], "false")
        self.assertEqual(output["message"],
                         "Another role with this name already exists.")

    def test_create_role_require_activity(self):
        """
        Tests creating a role
        Roles must have at least one activity
        """
        data_to_post = {}
        data_to_post['role_name'] = "TEST ROLE"
        response = self.client.post(reverse('api_create_role'), data_to_post)
        output = json.loads(response.content)
        self.assertEqual(output["success"], "false")
        self.assertEqual(output["message"],
                         "Each role must have at least one activity.")

    def test_create_role(self):
        """
        Tests creating a role
        """
        an_activity_id = self.role.activities.first().id

        data_to_post = {}
        data_to_post['role_name'] = "TEST ROLE"
        data_to_post['assigned_activities[]'] = [an_activity_id]
        response = self.client.post(reverse('api_create_role'), data_to_post)
        output = json.loads(response.content)
        self.assertEqual(output["success"], "true")

    def test_edit_role_require_post(self):
        """
        Tests editing a role
        Requires POST
        """
        expected_role_pk = self.role.pk

        data_to_post = {}
        data_to_post['role_name'] = "NEW ROLE NAME"
        response = self.client.get(reverse('api_edit_role',
                                           args=[expected_role_pk]),
                                   data_to_post)
        output = json.loads(response.content)
        self.assertEqual(output["success"], "false")
        self.assertEqual(output["message"], "POST method required.")

    def test_edit_role_require_activity(self):
        """
        Tests editing a role
        Requires at least one actvity
        """
        expected_role_pk = self.role.pk

        data_to_post = {}
        data_to_post['role_name'] = "NEW ROLE NAME"
        response = self.client.post(reverse('api_edit_role',
                                            args=[expected_role_pk]),
                                    data_to_post)
        output = json.loads(response.content)
        self.assertEqual(output["success"], "false")
        self.assertEqual(output["message"],
                         "At least one activity must be assigned.")

    def test_edit_role(self):
        """
        Tests editing a role
        """
        expected_role_pk = self.role.pk
        an_activity_id = self.role.activities.first().id

        data_to_post = {}
        data_to_post['role_name'] = "NEW ROLE NAME"
        data_to_post['assigned_activities[]'] = [an_activity_id]
        response = self.client.post(reverse('api_edit_role',
                                            args=[expected_role_pk]),
                                    data_to_post)
        output = json.loads(response.content)
        self.assertEqual(output["success"], "true")

    def test_delete_role_require_post(self):
        """
        Tests deleting a role
        Requires POST
        """
        expected_role_pk = self.role.pk

        response = self.client.get(reverse('api_delete_role',
                                           args=[expected_role_pk]))
        output = json.loads(response.content)
        self.assertEqual(output["success"], "false")
        self.assertEqual(output["message"], "DELETE method required.")

    def test_delete_role_role_most_exist(self):
        """
        Tests deleting a role
        Role must exist
        """
        response = self.client.delete(reverse('api_delete_role',
                                              args=[100000]))
        output = json.loads(response.content)
        self.assertEqual(output["success"], "false")

    def test_delete_role(self):
        """
        Tests deleting a role
        """
        expected_role_pk = self.role.pk

        # Should be able to delete an existing role
        response = self.client.delete(reverse('api_delete_role',
                                              args=[expected_role_pk]))
        output = json.loads(response.content)
        self.assertEqual(output["success"], "true")

    def test_get_all_roles(self):
        """
        Tests that api_get_all_roles returns data of the correct shape.

        """
        response = self.client.get(reverse('api_get_all_roles'))
        output = json.loads(response.content)

        role_shape = {
            'name': unicode,
            'activities': list,
        }
        for role in output.values():
            for key, value in role.items():
                self.assertEqual(type(value), role_shape[key])

                activity_shape = {
                    'id': int,
                    'name': unicode,
                    'appAccess': unicode,
                    'description': unicode
                }

                if key == 'activities':
                    for activity in value:
                        for k, v in activity.items():
                            self.assertEqual(type(v), activity_shape[k])

    def test_get_roles_contain_roles(self):
        """
        Tests that the Roles API returns the proper data in the
        proper form
        Contains role information
        """
        expected_role_pk = self.role.pk
        response = self.client.get(reverse('api_get_roles'))
        output = json.loads(response.content)
        first_result = output[0]

        role_id = first_result['role_id']
        self.assertIsInstance(role_id, int)

        role_name = first_result['role_name']
        self.assertIsInstance(role_name, unicode)

    def test_get_roles_contain_activities(self):
        """
        Tests that the Roles API returns the proper data in the
        proper form
        Contains activities information
        """
        expected_role_pk = self.role.pk

        response = self.client.get(reverse('api_get_roles'))
        output = json.loads(response.content)
        first_result = output[0]

        activities = first_result['activities']
        first_activity = activities[0]

        activity_app_access = first_activity['app_access_name']
        self.assertIsInstance(activity_app_access, unicode)

        available_activities = first_activity['available_activities']
        available_activity_name = available_activities[0]['name']
        self.assertIsInstance(available_activity_name, unicode)
        available_activity_id = available_activities[0]['id']
        self.assertIsInstance(available_activity_id, int)

        assigned_activities = first_activity['assigned_activities']
        assigned_activity_name = assigned_activities[0]['name']
        self.assertIsInstance(assigned_activity_name, unicode)
        assigned_activity_id = assigned_activities[0]['id']
        self.assertIsInstance(available_activity_id, int)

    def test_get_roles_contain_users(self):
        """
        Tests that the Roles API returns the proper data in the
        proper form
        Contains users information
        """

        expected_role_pk = self.role.pk

        response = self.client.get(reverse('api_get_roles'))
        output = json.loads(response.content)
        first_result = output[0]

        assigned_users = first_result['assigned_users']
        first_assigned_user = assigned_users[0]
        first_assigned_user_id = first_assigned_user['id']
        self.assertIsInstance(first_assigned_user_id, int)
        first_assigned_user_name = first_assigned_user['name']
        self.assertIsInstance(first_assigned_user_name, unicode)

        available_users = first_result['available_users']
        first_available_user = available_users[0]
        first_available_user_id = first_available_user['id']
        self.assertIsInstance(first_available_user_id, int)
        first_available_user_name = first_available_user['name']
        self.assertIsInstance(first_available_user_name, unicode)

    def test_get_specific_role_contains_role(self):
        """
        Tests that the Roles API returns the proper (specific role) data in the
        proper form
        Contain role
        """
        expected_role_pk = self.role.pk

        response = self.client.get(reverse('api_get_specific_role',
                                           args=[expected_role_pk]))
        output = json.loads(response.content)

        role_id = output['role_id']
        self.assertIsInstance(role_id, int)

        role_name = output['role_name']
        self.assertIsInstance(role_name, unicode)

    def test_get_specific_role_contains_activities(self):
        """
        Tests that the Roles API returns the proper (specific role) data in the
        proper form
        Contain activities
        """
        expected_role_pk = self.role.pk

        response = self.client.get(reverse('api_get_specific_role',
                                           args=[expected_role_pk]))
        output = json.loads(response.content)
        activities = output['activities']
        first_activity = activities[0]

        activity_app_access = first_activity['app_access_name']
        self.assertIsInstance(activity_app_access, unicode)

        available_activities = first_activity['available_activities']
        available_activity_name = available_activities[0]['name']
        self.assertIsInstance(available_activity_name, unicode)
        available_activity_id = available_activities[0]['id']
        self.assertIsInstance(available_activity_id, int)

        assigned_activities = first_activity['assigned_activities']
        assigned_activity_name = assigned_activities[0]['name']
        self.assertIsInstance(assigned_activity_name, unicode)
        assigned_activity_id = assigned_activities[0]['id']
        self.assertIsInstance(available_activity_id, int)

    def test_get_specific_role_activities_contain_app_access(self):
        """
        Tests that the Roles API returns the proper (specific role) data in the
        proper form
        Contain app_access
        """
        expected_role_pk = self.role.pk

        response = self.client.get(reverse('api_get_specific_role',
                                           args=[expected_role_pk]))
        output = json.loads(response.content)

        activities = output['activities']

        first_activity = activities[0]
        app_access_name = first_activity['app_access_name']
        self.assertIsInstance(app_access_name, unicode)

    def test_get_specific_role_contains_users(self):
        """
        Tests that the Roles API returns the proper (specific role) data in the
        proper form
        Contain users
        """
        expected_role_pk = self.role.pk

        response = self.client.get(reverse('api_get_specific_role',
                                           args=[expected_role_pk]))

        result = json.loads(response.content)

        assigned_users = result['assigned_users']
        first_assigned_user = assigned_users[0]
        first_assigned_user_id = first_assigned_user['id']
        self.assertIsInstance(first_assigned_user_id, int)
        first_assigned_user_name = first_assigned_user['name']
        self.assertIsInstance(first_assigned_user_name, unicode)

        available_users = result['available_users']
        first_available_user = available_users[0]
        first_available_user_id = first_available_user['id']
        self.assertIsInstance(first_available_user_id, int)
        first_available_user_name = first_available_user['name']
        self.assertIsInstance(first_available_user_name, unicode)

    def test_get_users(self):
        """
        Tests that the Users API returns the proper data in the proper form
        """
        expected_user_pk = self.user.pk

        response = self.client.get(reverse('api_get_users'))
        output = json.loads(response.content)

        # keys should be user ids associated with the company
        user_ids = list(self.company.role_set.filter(
            user__isnull=False).distinct().values_list('user__pk', flat=True))
        output_keys = [long(key) for key in output.keys()]
        self.assertEqual(output_keys, user_ids)

        # each entry should take a specific shape
        shape = {
            'email': unicode,
            'isVerified': bool,
            'lastInvitation': unicode,
            'roles': list,
        }

        for user in output.values():
            for key, value in user.items():
                self.assertTrue(type(value), shape[key])

    def test_create_user_require_post(self):
        """
        Tests creating a user
        Require POST
        """
        response = self.client.get(reverse('api_add_user'))
        self.assertEqual(response.status_code, 405)

    def test_create_user_user_must_have_role(self):
        """
        Tests creating a user
        Users must be assigned to at least one role
        """
        response = self.client.post(reverse('api_add_user'), {
            'email': 'andy@kaufman.com'
        })
        output = json.loads(response.content)
        self.assertIn(
            "Each user must be assigned to at least one role.",
            output["errors"])

    def test_create_user(self):
        """
        Tests creating a user
        """
        response = self.client.post(reverse('api_add_user'), {
            'email': 'andy@kaufman.com',
            'roles': [self.role.name]
        })
        output = json.loads(response.content)
        self.assertTrue(output['invited'])

    def test_create_user_keeps_roles(self):
        """
        Regression test. When attempting to add a user who already exists, that
        users existing roles would be overwritten. Instead, they should be
        added to.

        """
        self.user.roles = [self.role]
        self.assertItemsEqual(self.user.roles.all(), [self.role])
        role = RoleFactory(name='Test Role', company=self.company)

        self.client.post(reverse('api_add_user'), {
            'email': self.user.email,
            'roles': [role.name]
        })
        self.assertItemsEqual(self.user.roles.all(), [self.role, role])

    def test_add_role_to_existing_user(self):
        """
        Tests adding a role to an existing user
        """
        response = self.client.post(reverse('api_add_user'), data={
            'email': self.user.email,
            'roles': [self.role.name]
        })
        output = json.loads(response.content)
        self.assertFalse(output['invited'])

    def test_number_of_invitations_sent_on_role_addition(self):
        """
        Adding roles to a user should only send invitations for each of
        the new roles, not roles that were already attached.
        """
        new_role = RoleFactory(company=self.company)

        mail.outbox = []
        to_post = {
            'email': 'andy@kaufman.com',
            'roles': [self.role.name, new_role.name]
        }
        self.client.post(reverse('api_add_user'), to_post)
        message = "Expected {} invitations, found {}"
        self.assertEqual(len(mail.outbox), 2,
                         message.format(2, len(mail.outbox)))

        to_post['roles'].append(
            RoleFactory(company=self.company).name)
        self.client.post(reverse('api_add_user'), to_post)
        self.assertEqual(len(mail.outbox), 3,
                         message.format(3, len(mail.outbox)))

    def test_delete_user_require_post(self):
        """
        Tests deleting a user
        Require DELETE
        """
        response = self.client.get(reverse('api_remove_user',
                                           args=[self.user.pk]))
        self.assertEqual(response.status_code, 405)

    def test_delete_user(self):
        """
        Tests deleting a user

        """
        new_user = UserFactory(email='newuser@example.com',
                               roles=self.user.roles.all())

        response = self.client.delete(reverse('api_remove_user',
                                              args=[self.user.pk]))
        output = json.loads(response.content)
        self.assertEqual(output['errors'], [])

    def test_edit_user_require_post(self):
        """
        Tests editing a user
        Require POST
        """
        response = self.client.get(reverse('api_edit_user',
                                           args=[self.user.pk]))
        self.assertEqual(response.status_code, 405)

    def test_edit_user_user_must_exist(self):
        """
        Tests editing a user
        User must exist

        """
        # there weill never be a user with an ID of 0
        response = self.client.post(reverse('api_edit_user', args=[0]))
        output = json.loads(response.content)
        self.assertIn(u'User does not exist.', output['errors'])

    def test_edit_user(self):
        """
        Tests editing a user
        Edit user
        """
        expected_user_pk = self.user.pk

        role = RoleFactory(company=self.company, name='Test')

        response = self.client.post(
            reverse('api_edit_user', args=[self.user.pk]), {
                'add': [role.name],
            }
        )
        output = json.loads(response.content)
        self.assertEqual(
            output['errors'], [],"Editing a user shouldn't result in errors")
