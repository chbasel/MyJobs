from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

from myjobs.models import User


class CaseInsensitiveAuthBackend(ModelBackend):
    """
    We modify the user's email address when accounts are created.

    This causes issues if our modification is different than what
    the user typed  in.

    Override ModelBackground's `authenticate` method to allow for
    case-insensitive login
    """
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email__iexact=username)
            if user.is_locked_out():
                raise PermissionDenied("User is locked out")
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None


class CaseInsensitiveAuthFailCatcher(ModelBackend):
    """
    Note failed login attempts.

    This is meant to go last in the AUTHENTICATION_BACKENDS sequence.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email__iexact=username)
            user.note_failed_login()
        except User.DoesNotExist:
            return None
