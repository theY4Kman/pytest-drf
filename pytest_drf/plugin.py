from typing import Callable, TYPE_CHECKING

import pytest
from rest_framework.test import APIClient


if TYPE_CHECKING:
    from django.contrib.auth.models import User


@pytest.fixture
def create_drf_client() -> Callable[['User'], APIClient]:
    """A method returning a test client authenticated to the passed user

    To use a different test client class than the default DRF APIClient, or to
    customize how users are authenticated, override this fixture with your own
    implementation.
    """

    def create_drf_client(user: User) -> APIClient:
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    return create_drf_client
