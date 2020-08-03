from typing import Callable, TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    # NOTE: APIClient forward refs used to avoid loading Django settings too early
    from pytest_drf.client import DRFTestClient
    from django.contrib.auth.models import User


__all__ = ['create_drf_client', 'unauthed_client']


@pytest.fixture
def create_drf_client() -> Callable[['User'], 'DRFTestClient']:
    """A method returning a test client authenticated to the passed user

    To use a different test client class than the default DRF APIClient, or to
    customize how users are authenticated, override this fixture with your own
    implementation.
    """

    # NOTE: local import used to avoid loading Django settings too early
    from pytest_drf.client import DRFTestClient

    def create_drf_client(user: 'User') -> 'DRFTestClient':
        client = DRFTestClient()
        client.force_authenticate(user=user)
        return client

    return create_drf_client


@pytest.fixture
def unauthed_client() -> 'DRFTestClient':
    """A DRF test client with no authentication"""

    # NOTE: local import used to avoid loading Django settings too early
    from pytest_drf.client import DRFTestClient

    return DRFTestClient()
