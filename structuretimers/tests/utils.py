from packaging.version import Version

from django import get_version as django_get_version
from django.contrib.auth.models import User

from allianceauth.tests.auth_utils import AuthUtils

_is_aa4 = Version(django_get_version()) >= Version("4.2")


def add_permission_to_user_by_name(perm: str, user: User) -> User:
    """adds permission to given user by name and returns updated user object"""
    AuthUtils.add_permission_to_user_by_name(perm, user)
    return User.objects.get(pk=user.pk)
