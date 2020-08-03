"""
Testing Views and ViewSets
==========================

This module contains the APIViewTest and ViewSetTest base classes for testing
Django REST framework's APIViews and ViewSets, respectively; as well, other
mixins are exposed for declaring which HTTP method is used, and for ViewSetTests,
which endpoint is used.

"""
from typing import Dict, Any
from urllib.parse import ParseResult, urlparse, parse_qs, urlencode, urlunparse

import pytest
from pytest_common_subject import CommonSubjectTestMixin
from pytest_lambda import lambda_fixture, static_fixture

from pytest_drf.util import deprioritize_base

__all__ = [
    'APIViewTest',
    'ViewSetTest',
    'UsesListEndpoint',
    'UsesDetailEndpoint',
    'UsesGetMethod',
    'UsesPostMethod',
    'UsesPutMethod',
    'UsesPatchMethod',
    'UsesDeleteMethod',
]


@deprioritize_base
class APIViewTest(CommonSubjectTestMixin):
    """Base class providing default fixtures for DRF API views

    Be sure to subclass this in any viewset tests using the APITest harness.
    By requiring this instead of defining fixtures inside APITest,
    parametrization can be used to override fixtures, avoiding large subclasses
    """

    @pytest.fixture
    def client(self, unauthed_client):
        """API client to perform requests with

        If you require a particular user to be authenticated, set this fixture
        to a different client (e.g. "admin_client"):

            @pytest.fixture
            def client(admin_client):
                return admin_client

            # This can also be expressed more compactly with lambda_fixture
            client = lambda_fixture('admin_client')

        The AsUser(user_fixture_name) mixin will override `client` with an
        API client authenticated to the User from the specified
        user_fixture_name:

            class TestMyAPIView(APIViewTest, AsUser('admin')):
                pass

        Or, perform authentication yourself:

            @pytest.fixture
            def client(unauthed_client, my_user):
                unauthed_client.force_authenticate(user=my_user)
                return unauthed_client

        """
        return unauthed_client

    @pytest.fixture
    def http_method(self):
        """Name of API client method to perform request with"""
        return 'get'

    @pytest.fixture
    def url(self):
        """Base URL to be requested

        Use reverse() to generate URLs:

            @pytest.fixture
            def url():
                return reverse('viewset_basename-list')

            # This can also be expressed more compactly with lambda_fixture
            url = lambda_fixture(lambda: reverse('viewset_basename-list'))

            # Other fixtures can be requested to use in URL generation:
            url = lambda_fixture(lambda vendor: reverse('vendors-detail',
                                                        args=(vendor.pk,)))

        """
        raise NotImplementedError('Please define a url fixture')

    @pytest.fixture
    def query_params(self) -> Dict[str, Any]:
        """Extra query params to tack onto url"""
        return {}

    @pytest.fixture
    def full_url(self, url, query_params) -> str:
        """Base URL with query params appended
        """
        if not query_params:
            return url

        parsed_url: ParseResult = urlparse(url)

        parsed_qs = parse_qs(parsed_url.query)
        parsed_qs.update(query_params)

        full_query = urlencode(parsed_qs)
        full_url_parts = parsed_url._replace(query=full_query)
        full_url = urlunparse(full_url_parts)

        return full_url

    @pytest.fixture
    def headers(self):
        """Headers to pass along with the request"""
        return {}

    @pytest.fixture
    def data(self):
        """Data to send to the server with the request."""

    @pytest.fixture
    def get_response(self, http_method, client):
        """API client test method called to perform actual request"""
        return getattr(client, http_method)

    @pytest.fixture
    def response(self, common_subject_rval):
        """Response from server; the result of calling the API client method"""
        return common_subject_rval

    @pytest.fixture
    def json(self, response):
        """The JSON body of the API response"""
        return response.json()

    @pytest.fixture
    def results(self, json):
        """The value of the 'results' key in the API response JSON body"""
        return json['results']

    # Configuration for CommonSubjectTestMixin below

    @pytest.fixture
    def common_subject(self, get_response):
        return get_response

    @pytest.fixture
    def args(self, full_url):
        return (full_url,)

    @pytest.fixture
    def kwargs(self, data, headers):
        return dict(data=data, headers=headers)


class ViewSetTest(APIViewTest):
    """DRF view test w/ ViewSet-specific conveniences"""

    @pytest.fixture
    def list_url(self):
        """Return the list URL for the viewset. See UseListEndpoint"""
        raise NotImplementedError('Please define a list_url fixture')

    @pytest.fixture
    def detail_url(self):
        """Return the detail URL for the viewset. See UseDetailEndpoint"""
        raise NotImplementedError('Please define a detail_url fixture')


######################
# URL / PATH / ROUTE #
######################
#
# Declare which ViewSet URL route to request


class UsesListEndpoint:
    url = lambda_fixture('list_url')


class UsesDetailEndpoint:
    url = lambda_fixture('detail_url')


###############
# HTTP METHOD #
###############
#
# Declare which HTTP method used when performing the request - more specifically,
# which method on the test client is called.


class UsesGetMethod:
    http_method = static_fixture('get')


class UsesPostMethod:
    http_method = static_fixture('post')


class UsesPutMethod:
    http_method = static_fixture('put')


class UsesPatchMethod:
    http_method = static_fixture('patch')


class UsesDeleteMethod:
    http_method = static_fixture('delete')
