"""
Declaring the authenticated user
================================

This module contains test mixins for declaring which user is authenticated when
making requests.

"""
from typing import Type

import inflection
import pytest
from pytest_lambda import lambda_fixture

__all__ = [
    'AsUser',
    'AsAnonymousUser',
]


##################
# AUTHENTICATION #
##################
#
# Declare what kind of authenticated user will perform the request


class _AsUserMeta(type):
    # This metaclass allows AsUser('my_user') to return a test mixin with the
    # client fixture authenticated as `my_user`

    def __call__(cls, *args, **kwargs) -> Type['AsUser']:
        if cls is not AsUser:
            return super().__call__(*args, **kwargs)

        user_fixture_name, = args

        class AsUserXYZ:
            f"""Authenticates the `client` fixture to {user_fixture_name}
            """

            @pytest.fixture
            def client(self, create_drf_client, client_user):
                return create_drf_client(client_user)

            client_user = lambda_fixture(user_fixture_name)

        user_fixture_title = inflection.camelize(user_fixture_name)
        return type(f'As{user_fixture_title}', (AsUserXYZ,), {})


class AsUser(metaclass=_AsUserMeta):
    """Authenticates the `client` fixture to the user fixture named in the constructor
    """

    @pytest.fixture
    def client(self):
        raise NotImplementedError()

    @pytest.fixture
    def client_user(self):
        raise NotImplementedError()

    # this appeases code sense, which may not be able to understand how the
    # metaclass allows using instantiation syntax without really instantiating.
    def __init__(self, fixture_name: str):
        pass

    del __init__


class AsAnonymousUser:
    client = lambda_fixture('unauthed_client')
