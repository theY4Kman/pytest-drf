"""
Enforcing access control based on user type
===========================================

This module contains test mixins to declare which types of users should not be
able to access a resource.

"""
from pytest_drf.authentication import AsAnonymousUser
from pytest_drf.status import Returns401

__all__ = ['ForbidsAnonymousUsers']


class ForbidsAnonymousUsers:
    class TestForbidsAnonymousUser(Returns401, AsAnonymousUser):
        pass
