from django.urls import reverse
from pytest_lambda import lambda_fixture

from pytest_drf import (
    APIViewTest,
    ReturnsCursorPagination,
    ReturnsLimitOffsetPagination,
    ReturnsPageNumberPagination,
    UsesGetMethod,
)


class DescibePageNumberPaginationView(
    APIViewTest,
    UsesGetMethod,

    ReturnsPageNumberPagination,
):
    url = lambda_fixture(lambda: reverse('pagination-page-number'))


class DescibeLimitOffsetPaginationView(
    APIViewTest,
    UsesGetMethod,

    ReturnsLimitOffsetPagination,
):
    url = lambda_fixture(lambda: reverse('pagination-limit-offset'))


class DescibeCursorPaginationView(
    APIViewTest,
    UsesGetMethod,

    ReturnsCursorPagination,
):
    url = lambda_fixture(lambda: reverse('pagination-cursor'))
