"""
Enforcing HTTP status codes
===========================

This module contains test mixins to declare the HTTP status code expected in
an API response

"""
from typing import Type

import pytest
from pytest_lambda import static_fixture
from rest_framework import status

__all__ = [
    'ReturnsStatus',
    'Returns200',
    'Returns201',
    'Returns202',
    'Returns204',
    'Returns301',
    'Returns302',
    'Returns304',
    'Returns307',
    'Returns308',
    'Returns400',
    'Returns401',
    'Returns403',
    'Returns404',
    'Returns405',
    'Returns409',
    'Returns422',
    'Returns429',
    'Returns500',
    'Returns503',
    'Returns504',
]


class _ReturnsSpecificStatusMeta(type):
    # This metaclass allows ReturnStatus(xyz) to return a subclass of
    # ReturnStatus with the expected_status_code fixture defined as xyz.

    def __call__(cls, *args, **kwargs) -> Type['ReturnsStatus']:
        if cls is not ReturnsStatus:
            return super().__call__(*args, **kwargs)

        status_code, = args

        # We create a copy of this method, so we can change its name to
        # include the expected status code.
        def it_returns_expected_status_code(self, response, expected_status_code):
            expected = expected_status_code
            actual = response.status_code
            assert expected == actual

        it_returns_expected_status_code.__name__ = f'it_returns_{status_code}'

        returns_code_cls = type(f'Returns{status_code}', (), {
            f'it_returns_{status_code}': it_returns_expected_status_code,
            it_returns_expected_status_code.__name__: it_returns_expected_status_code,
            'expected_status_code': static_fixture(status_code),

            # Disable the original method
            'it_returns_expected_status_code': None,
        })
        return returns_code_cls


class ReturnsStatus(metaclass=_ReturnsSpecificStatusMeta):
    """Includes test which checks response for the HTTP specified status code
    """

    @pytest.fixture
    def expected_status_code(self):
        raise NotImplementedError(
            'Please define the expected_status_code fixture. Alternatively, '
            'subclass ReturnStatus(code) instead of the bare ReturnStatus.'
        )

    def it_returns_expected_status_code(self, response, expected_status_code):
        expected = expected_status_code
        actual = response.status_code
        assert expected == actual

    # this appeases code sense, which may not be able to understand how the
    # metaclass allows using instantiation syntax without really instantiating.
    def __init__(self, status_code: int):
        pass

    del __init__


# 2xx Success
Returns200 = ReturnsStatus(status.HTTP_200_OK)
Returns201 = ReturnsStatus(status.HTTP_201_CREATED)
Returns202 = ReturnsStatus(status.HTTP_202_ACCEPTED)
Returns204 = ReturnsStatus(status.HTTP_204_NO_CONTENT)

# 3xx Redirection
Returns301 = ReturnsStatus(status.HTTP_301_MOVED_PERMANENTLY)
Returns302 = ReturnsStatus(status.HTTP_302_FOUND)
Returns304 = ReturnsStatus(status.HTTP_304_NOT_MODIFIED)
Returns307 = ReturnsStatus(status.HTTP_307_TEMPORARY_REDIRECT)
Returns308 = ReturnsStatus(status.HTTP_308_PERMANENT_REDIRECT)

# 4xx Client errors
Returns400 = ReturnsStatus(status.HTTP_400_BAD_REQUEST)
Returns401 = ReturnsStatus(status.HTTP_401_UNAUTHORIZED)
Returns403 = ReturnsStatus(status.HTTP_403_FORBIDDEN)
Returns404 = ReturnsStatus(status.HTTP_404_NOT_FOUND)
Returns405 = ReturnsStatus(status.HTTP_405_METHOD_NOT_ALLOWED)
Returns409 = ReturnsStatus(status.HTTP_409_CONFLICT)
Returns422 = ReturnsStatus(status.HTTP_422_UNPROCESSABLE_ENTITY)
Returns429 = ReturnsStatus(status.HTTP_429_TOO_MANY_REQUESTS)

# 5xx Server errors
Returns500 = ReturnsStatus(status.HTTP_500_INTERNAL_SERVER_ERROR)
Returns503 = ReturnsStatus(status.HTTP_503_SERVICE_UNAVAILABLE)
Returns504 = ReturnsStatus(status.HTTP_504_GATEWAY_TIMEOUT)
