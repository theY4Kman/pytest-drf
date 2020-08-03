from django.contrib.auth.models import User
from django.urls import reverse
from pytest_lambda import lambda_fixture

from pytest_drf import (
    APIViewTest,
    AsUser,
    ForbidsAnonymousUsers,
    Returns200,
    UsesGetMethod,
)


user = lambda_fixture(lambda db: User.objects.create(
    username='user',
    first_name='Test',
    last_name='User',
    email='test@us.er',
))


class DescribeLoginRequired(
    APIViewTest,
    UsesGetMethod,

    ForbidsAnonymousUsers,

    AsUser('user'),
    Returns200,
):
    # NOTE: this view simply returns 200, but requires an authenticated user
    #       (i.e. it declares IsAuthenticated for its permission_classes)
    url = lambda_fixture(lambda: reverse('authorization-login-required'))

