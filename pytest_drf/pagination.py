"""
Enforce the use of pagination
=============================

Test mixins to declare the structure of paginated responses.

"""
from pytest_assert_utils import util


class ReturnsPageNumberPagination:
    def it_returns_page_number_pagination_format(self, json):
        expected = {
            'count': util.Any(int),
            'next': util.Optional(util.Any(str)),
            'previous': util.Optional(util.Any(str)),
            'results': util.Any(list),
        }
        actual = json
        assert actual == expected, 'Response is not in PageNumberPagination format'


class ReturnsLimitOffsetPagination:
    def it_returns_limit_offset_pagination_format(self, json):
        expected = {
            'count': util.Any(int),
            'next': util.Optional(util.Any(str)),
            'previous': util.Optional(util.Any(str)),
            'results': util.Any(list),
        }
        actual = json
        assert actual == expected, 'Response is not in LimitOffsetPagination format'


class ReturnsCursorPagination:
    def it_returns_cursor_pagination_format(self, json):
        expected = {
            'next': util.Optional(util.Any(str)),
            'previous': util.Optional(util.Any(str)),
            'results': util.Any(list),
        }
        actual = json
        assert actual == expected, 'Response is not in CursorPagination format'
