"""Tests for various universal helpers."""
from mysearches.tests.factories import SavedSearchFactory
from myjobs.tests.factories import RoleFactory
from myjobs.tests.setup import MyJobsBase
from universal.helpers import invitation_context


class InvitationContextTests(MyJobsBase):
    """Tests for the generic invitation_context function."""
    def test_saved_search_invitation_context(self):
        """
        Test that creating an invitation context from a saved search instance
        produces a context with a message, the saved search itself, an unsent
        initial email, and whether that saved search is text only.

        """
        saved_search = SavedSearchFactory(user=self.user, text_only=True)
        context = invitation_context(saved_search)

        self.assertEqual(context, {
            "message": " in order to begin receiving their available job "
                       "opportunities on a regular basis.",
            "saved_search": saved_search,
            "initial_search_email": saved_search.initial_email(send=False),
            "text_only": saved_search.text_only})

    def test_str_invitation_context(self):
        """
        Test that creating an invitation context from a string
        produces a context with a message.

        """
        context = invitation_context("This is a test")
        self.assertEqual(context, {"message": " This is a test."})

    def test_role_invitation_context(self):
        """
        Test that reating an invitation context from a role instance produces
        a context with a message and the role itself.
        """
        role = RoleFactory()
        context = invitation_context(role)
        self.assertEqual(context, {
            "message": " as a(n) %s for %s." % (role.name, role.company),
            "role": role})

    def test_unimplemented_invitation_context(self):
        """
        Test that trying to call invitation_context for an unregistered type
        should raise a sensible error.
        """

        with self.assertRaises(TypeError) as cm:
            context = invitation_context(None)

        self.assertEqual(
            cm.exception.message,
            "object of type 'NoneType' has no invitation_context.")
