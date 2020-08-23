from pytest_lambda import lambda_fixture

from pytest_drf import (
    APIViewTest,
    ReturnsCursorPagination,
    ReturnsLimitOffsetPagination,
    ReturnsPageNumberPagination,
    UsesGetMethod,
)
from pytest_drf.util import url_for


class DescibePageNumberPaginationView(
    APIViewTest,
    UsesGetMethod,

    ReturnsPageNumberPagination,
):
    url = lambda_fixture(lambda: url_for('pagination-page-number'))


class DescibeLimitOffsetPaginationView(
    APIViewTest,
    UsesGetMethod,

    ReturnsLimitOffsetPagination,
):
    url = lambda_fixture(lambda: url_for('pagination-limit-offset'))


class DescibeCursorPaginationView(
    APIViewTest,
    UsesGetMethod,

    ReturnsCursorPagination,
):
    url = lambda_fixture(lambda: url_for('pagination-cursor'))
