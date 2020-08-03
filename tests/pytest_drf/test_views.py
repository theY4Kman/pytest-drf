from typing import Any, Dict

import pytest
from django.urls import reverse
from pytest_assert_utils import assert_dict_is_subset, assert_model_attrs
from pytest_common_subject import precondition_fixture
from pytest_lambda import lambda_fixture, static_fixture

from pytest_drf import (
    APIViewTest,
    Returns200,
    Returns201, Returns204, UsesDeleteMethod, UsesDetailEndpoint, UsesGetMethod,
    UsesListEndpoint,
    UsesPatchMethod, UsesPostMethod,
    ViewSetTest,
)
from pytest_drf.util import pluralized
from tests.example_project.models import KeyValue


class DescribeQueryParams(
    APIViewTest,
    UsesGetMethod,
):
    # NOTE: this view simply returns the request's query params as the response
    url = lambda_fixture(lambda: reverse('views-query-params'))

    # This fixture supports passing query params (e.g. ?key=val) with the requested URL
    query_params = static_fixture({
        'key': 'val',
        'param': 'value',
        'pink': 'floyd',
    })


    def it_passes_query_params(self, json, query_params):
        expected = query_params
        actual = json
        assert expected == actual


class DescribeHeaders(
    APIViewTest,
    UsesGetMethod,
):
    # NOTE: this view simply returns the request's headers as the response
    url = lambda_fixture(lambda: reverse('views-headers'))

    # This fixture supports passing headers (e.g. `Authorization: Api-Key 123`) in the request
    headers = static_fixture({
        'Custom-Header': 'abc',
        'Head': 'Shoulders, Knees, Toes',
    })


    def it_passes_headers(self, json, headers):
        expected = headers
        actual = json
        assert_dict_is_subset(expected, actual)


class DescribeData(
    APIViewTest,
    UsesPostMethod,
):
    # NOTE: this view simply returns the request's POST data as the response
    url = lambda_fixture(lambda: reverse('views-data'))

    # This fixture supports passing POST data in the request
    data = static_fixture({
        'post': 'malone',
        'fizzbuzz': 'zibbzuff',
    })


    def it_posts_data(self, json, data):
        expected = data
        actual = json
        assert expected == actual


def express_key_value(kv: KeyValue) -> Dict[str, Any]:
    """Return the expected API representation of a KeyValue

    Expression methods can be a handy tool for API scaffolding. Instead of
    focusing on how to create a certain representation using serializers and
    fields, an expression method enables one to simply consider which
    information they'd like available from an endpoint, and implement it by
    whatever means are convenient. After the expression method is created, one
    can focus all their attention on writing a beautiful, maintainable serializer.
    """
    return {
        'id': kv.id,
        'key': kv.key,
        'value': kv.value,
    }


###
# Expression methods only accept a single model/object. When dealing with list
# endpoints, we often have a list of models/objects. For this situation,
# the `pluralized` method/decorator converts our single-object expression
# method into a pluralized version that accepts lists of objects. The pluralized
# method will then call our expression method on each object in the passed list,
# and return the expressed versions as a list, in the same order.
#
express_key_values = pluralized(express_key_value)


@pytest.mark.django_db
class DescribeKeyValueViewSet(ViewSetTest):
    list_url = lambda_fixture(
        lambda:
            reverse('views-key-values-list'))

    detail_url = lambda_fixture(
        lambda key_value:
            reverse('views-key-values-detail', kwargs={'pk': key_value.pk}))


    class DescribeList(
        UsesGetMethod,
        UsesListEndpoint,

        Returns200,
    ):
        # Here, we create some rows in the DB to play with. We set autouse=True,
        # so the fixture is evaluated even though nothing explicitly requests it.
        # The @pytest.mark.late (from pytest-fixture-order) mark ensures our
        # http request is run *after* all autouse fixtures.
        key_values = lambda_fixture(
            lambda: (
                KeyValue.objects.create_batch(
                    alpha='beta',
                    delta='gamma',
                )
            ),
            autouse=True,
        )


        def it_returns_key_values_rows(self, key_values, results):
            expected = express_key_values(key_values)
            actual = results
            assert expected == actual


    class DescribeCreate(
        UsesPostMethod,
        UsesListEndpoint,

        Returns201,
    ):
        data = static_fixture({
            'key': 'apple',
            'value': 'π',
        })

        ###
        # precondition_fixture uses the pytest dependency graph to ensure that,
        # if requested, this fixture is *always* evaluated before our HTTP request
        # is made.
        #
        # Here, we record the existing KeyValue IDs, so we can verify that a
        # new row was indeed created by our endpoint.
        #
        initial_key_value_ids = precondition_fixture(
            lambda:
                set(KeyValue.objects.values_list('pk', flat=True)))


        def it_creates_key_value(self, initial_key_value_ids, json):
            expected = initial_key_value_ids | {json['id']}
            actual = set(KeyValue.objects.values_list('pk', flat=True))
            assert expected == actual

        def it_returns_key_value(self, json):
            key_value = KeyValue.objects.get(pk=json['id'])

            expected = express_key_value(key_value)
            actual = json
            assert expected == actual

        def it_sets_model_fields(self, data, json):
            key_value = KeyValue.objects.get(pk=json['id'])

            expected = data
            assert_model_attrs(key_value, expected)


    class DescribeRetrieve(
        UsesGetMethod,
        UsesDetailEndpoint,

        Returns200,
    ):
        # NOTE: autouse=True is not used, because the detail_url requests this
        #       fixture
        key_value = lambda_fixture(
            lambda:
                KeyValue.objects.create(
                    key='apple',
                    value='π',
                ))


        def it_returns_key_value(self, key_value, json):
            expected = express_key_value(key_value)
            actual = json
            assert expected == actual


    class DescribeUpdate(
        UsesPatchMethod,
        UsesDetailEndpoint,

        Returns200,
    ):
        # NOTE: autouse=True is not used, because the detail_url requests this
        #       fixture
        key_value = lambda_fixture(
            lambda:
                KeyValue.objects.create(
                    key='apple',
                    value='π',
                ))

        data = static_fixture({
            'key': 'banana',
            'value': 'ρ',
        })

        ###
        # precondition_fixture uses the pytest dependency graph to ensure that,
        # if requested, this fixture is *always* evaluated before our HTTP request
        # is made.
        #
        # Here, we record the existing KeyValue IDs, so we can verify that no
        # new rows are created by our endpoint. We request the `key_value` fixture,
        # to ensure it's included in this set.
        #
        initial_key_value_ids = precondition_fixture(
            lambda key_value:
                set(KeyValue.objects.values_list('pk', flat=True)))


        def it_updates_key_value(self, key_value, data):
            # After updating, refreshing our DB row is vital — otherwise, it
            # will appear as though our endpoint is not doing its job.
            key_value.refresh_from_db()

            expected = data
            assert_model_attrs(key_value, expected)

        def it_returns_key_value(self, key_value, json):
            # After updating, refreshing our DB row is vital — otherwise, it
            # will appear as though our endpoint is not doing its job.
            key_value.refresh_from_db()

            expected = express_key_value(key_value)
            actual = json
            assert expected == actual

        def it_doesnt_create_or_destroy_rows(self, initial_key_value_ids):
            expected = initial_key_value_ids
            actual = set(KeyValue.objects.values_list('pk', flat=True))
            assert expected == actual


    class DescribeDestroy(
        UsesDeleteMethod,
        UsesDetailEndpoint,

        Returns204,
    ):
        # NOTE: autouse=True is not used, because the detail_url requests this
        #       fixture
        key_value = lambda_fixture(
            lambda:
                KeyValue.objects.create(
                    key='apple',
                    value='π',
                ))

        ###
        # precondition_fixture uses the pytest dependency graph to ensure that,
        # if requested, this fixture is *always* evaluated before our HTTP request
        # is made.
        #
        # Here, we record the existing KeyValue IDs, so we can verify that our
        # endpoint actually deletes the row
        #
        initial_key_value_ids = precondition_fixture(
            lambda:
                set(KeyValue.objects.values_list('pk', flat=True)))


        def it_deletes_key_value(self, key_value, initial_key_value_ids):
            expected = initial_key_value_ids - {key_value.id}
            actual = set(KeyValue.objects.values_list('pk', flat=True))
            assert expected == actual
