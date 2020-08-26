# pytest-drf

[![PyPI version](https://badge.fury.io/py/pytest-drf.svg)](https://badge.fury.io/py/pytest-drf)
[![Build Status](https://travis-ci.org/theY4Kman/pytest-drf.svg?branch=master)](https://travis-ci.org/theY4Kman/pytest-drf)

pytest-drf is a [pytest](http://pytest.org) plugin for testing your [Django REST Framework](https://www.django-rest-framework.org/) APIs.


# Installation

```bash
pip install pytest-drf
```


# The Spiel

pytest-drf aims to shoo away clunky setup code and boilerplate in DRF tests, in favor of declarative scaffolds and configurable fixtures encouraging small, easy-to-follow tests with single responsibilities.

This is accomplished by performing one request per test, and providing the response as a fixture. All configuration of the request — the URL, the query params, the HTTP method, the POST data, etc — is also done through fixtures. This frees the test methods to contain only assertions about the response or the state of the app after the request completes.

For example, consider a public API endpoint that responds to a GET request with the JSON string "Hello, World!" and a 200 status code. Such an endpoint might be written like so

```python
# example/views.py

from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

@api_view()
@permission_classes([permissions.AllowAny])
def hello_world(request):
    return Response('Hello, World!')
```

Let's route it to `/hello`, and give it a name, so we can easily generate URLs for it.

```python
# example/urls.py

from django.urls import path

from example import views

urlpatterns = [
    path('hello', views.hello_world, name='hello-world'),
]
```

With pytest-drf, we'd verify the behavior of our endpoint with something like this

```python
# tests/test_hello.py

import pytest
from django.urls import reverse
from pytest_drf import APIViewTest, Returns200, UsesGetMethod

class TestHelloWorld(
    APIViewTest,
    UsesGetMethod,
    Returns200,
):
    @pytest.fixture
    def url(self):
        return reverse('hello-world')

    def test_it_returns_hello_world(self, json):
        expected = 'Hello, World!'
        actual = json
        assert expected == actual
```

When we run pytest, we see two tests run

```
$ py.test

tests/test_hello.py::TestHelloWorld::test_it_returns_200 <- pytest_drf/status.py PASSED [ 50%]
tests/test_hello.py::TestHelloWorld::test_it_returns_hello_world PASSED                 [100%]
```


### What happened here? 

Well, `APIViewTest` defines a `response` fixture that takes the value of the `url` fixture and makes an HTTP request to it. The `UsesGetMethod` mixin defines the `http_method` as `'get'`, making it a GET request. The `response` fixture is defined as `autouse=True`, so it's automatically evaluated before the test method is executed.

The `Returns200` mixin simply adds a test with `assert response.status_code == 200`. This test has its own request/response cycle, independent of `test_it_returns_hello_world` — this way, if the endpoint responds with the wrong status code but the correct response data, one can see what needs fixing after running `py.test` only once!


### What's with the `json` fixture?

Why does `test_it_returns_hello_world` use the `json` fixture, instead of `response`?

`json` is another fixture that merely returns `response.json()`. Because the API response is provided as a fixture, we can perform any post-processing transformations on it in another fixture — this lets us keep all those irrelevant implementation details out of the test methods, so they can focus on one thing and one thing only: verifying the data is correct.


### Do I have to use this `expected == actual` business?

No, but it's Encouraged™! By explicitly labeling the known value and the value being tested, it'll be easier for another reader (including future you) to understand what's actually going on.

The specific order of `expected` and `actual` in the assertion (i.e. whether it's `expected == actual` or `actual == expected`) isn't as important as maintaining the same order everywhere. This will ease the interpretation of test failures, as, e.g., you'll always know which side of a diff contains the incorrect values.

The order `expected == actual` is used in pytest-drf's mixins to serve a left-to-right bias, where `expected == actual` always puts the known value first.


### Reducing the bulkiness of fixtures

Though a fixture-based approach like this can be very convenient in terms of configuration and hiding implementation details, it can also consume a lot of valuable screen real estate — especially if the fixtures consist entirely of a return statement.

For simple, one-line fixtures, [pytest-lambda](https://github.com/they4kman/pytest-lambda) (included as a dependency to pytest-drf) enables expressing them as lambda functions. Here's what our test file looks like with a lambda fixture

```python
from django.urls import reverse
from pytest_drf import APIViewTest, Returns200, UsesGetMethod
from pytest_lambda import lambda_fixture

class TestHelloWorld(
    APIViewTest,
    UsesGetMethod,
    Returns200,
):
    url = lambda_fixture(lambda: reverse('hello-world'))

    def test_it_returns_hello_world(self, json):
        expected = 'Hello, World!'
        actual = json
        assert expected == actual
```

Additionally, for constant value fixtures, pytest-lambda provides `static_fixture`

```python

```


## What about authentication?

To make requests as someone other than `AnonymousUser`, pytest-drf provides the `AsUser()` mixin. Simply create / expose a user in a fixture, and include the mixin with your view test

```python
from django.contrib.auth.models import User
from django.urls import reverse
from pytest_drf import APIViewTest, AsUser, Returns200, UsesGetMethod
from pytest_lambda import lambda_fixture

alice = lambda_fixture(
    lambda: User.objects.create(
        username='alice',
        first_name='Alice',
        last_name='Innchains',
        email='alice@ali.ce',
    ))

class TestAboutMe(
    APIViewTest,
    UsesGetMethod,
    Returns200,
    AsUser('alice'),
):
    url = lambda_fixture(lambda: reverse('about-me'))

    def test_it_returns_profile(self, json):
        expected = {
            'username': 'alice',
            'first_name': 'Alice',
            'last_name': 'Innchains',
            'email': 'alice@ali.ce',
        }
        actual = json
        assert expected == actual
```


## But I mainly use ViewSets, not APIViews!

pytest-drf offers `ViewSetTest`, along with some mixins and conventions, to aid in testing ViewSets. 

Consider this `KeyValue` model. It's got an ID, a string key, and a string value 

```python
# kv/models.py

from django.db import models

class KeyValue(models.Model):
    key = models.CharField(max_length=32, unique=True)
    value = models.CharField(max_length=32)
```

We implement the endpoints with a `ModelViewSet` and `ModelSerializer`

```python
# kv/views.py

from rest_framework import permissions, serializers, viewsets
from rest_framework.pagination import PageNumberPagination

from kv.models import KeyValue

class KeyValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyValue
        fields = (
            'id',
            'key',
            'value',
        )

class KeyValueViewSet(viewsets.ModelViewSet):
    queryset = KeyValue.objects.order_by('id')
    serializer_class = KeyValueSerializer
    pagination_class = PageNumberPagination
    permission_classes = [permissions.AllowAny]
```

We route it with a base path of `/kv`, leading to the registration of two routes (list and detail) servicing list, create, retrieve, update, and destroy actions

 - `GET /kv` — list KeyValues
 - `POST /kv` — create a KeyValue
 - `GET /kv/<pk>` — retrieve a KeyValue
 - `PATCH /kv/<pk>` — update a KeyValue
 - `DELETE /kv/<pk>` — delete a KeyValue

```python
# kv/urls.py

from django.urls import include, path
from rest_framework import routers

from kv import views

router = routers.DefaultRouter()
router.register('kv', views.KeyValueViewSet, basename='key-values')

urlpatterns = [
    path('', include(router.urls)),
]
```

Now, using `ViewSetTest`, we scaffold our tests

```python
# tests/test_kv.py

from pytest_drf import (
    ViewSetTest,
    Returns200,
    Returns201,
    Returns204,
    UsesGetMethod,
    UsesDeleteMethod,
    UsesDetailEndpoint,
    UsesListEndpoint,
    UsesPatchMethod,
    UsesPostMethod,
)
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture

class TestKeyValueViewSet(ViewSetTest):
    list_url = lambda_fixture(
        lambda:
            url_for('key-values-list'))

    detail_url = lambda_fixture(
        lambda key_value:
            url_for('key-values-detail', key_value.pk))

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        pass

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        pass

    class TestRetrieve(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        pass

    class TestUpdate(
        UsesPatchMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        pass

    class TestDestroy(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        Returns204,
    ):
        pass
```

At the moment, most of these tests will fail, because we haven't yet provided an implementation for the `key_value` fixture (though, `TestCreate` fails on serializer validation, as we haven't passed any required fields, yet).

```bash
$ py.test --tb=no

tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_200 <- pytest_drf/status.py PASSED    [ 20%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_201 <- pytest_drf/status.py FAILED  [ 40%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_200 <- pytest_drf/status.py ERROR [ 60%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_returns_200 <- pytest_drf/status.py ERROR   [ 80%]
tests/test_kv.py::TestKeyValueViewSet::TestDestroy::test_it_returns_204 <- pytest_drf/status.py ERROR  [100%]
```

The skeleton above, which we'll fill out soon, is just to show the key components of a `ViewSetTest`, which are:


### Implementing `list_url` and `detail_url`

Unlike APIViews, ViewSets often have two separate routes: one for the general set of resources (the list endpoint), and one for a specific resource (the detail endpoint). Since these are the same URLs regardless of the particular ViewSet action, we implement them once at the beginning of the ViewSetTest, and switch between them in nested classes using `UsesListEndpoint` and `UsesDetailEndpoint`.

Since the detail endpoint acts upon a specific instance, `detail_url` acts upon the `key_value` fixture, which we will implement in the Retrieve/Update/Destroy tests by creating a `KeyValue` row.


### ViewSet action child test contexts (nested classes)

For each ViewSet action (i.e. endpoint/http method combination), we'll create a separate nested class (AKA test context) with appropriate mixins to denote which endpoint to hit (implemented by `list_url` or `detail_url`), and with which HTTP method. We also add a `Returns2XX` mixin for each endpoint, which quickly lets us run tests that hit the actual ViewSet.

Now, before we get to writing the crux of our CRUD tests, we're gonna implement an _expression method_, which will aid us in verifying API responses.
 
### Expression methods

An expression method is a simple function that takes a model instance and returns what the API would respond for it. Our serializer has three fields: `id`, `key`, and `value`. So our expression method looks something like this:

```python
def express_key_value(kv: KeyValue) -> Dict[str, Any]:
    return {
        'id': kv.id,
        'key': kv.key,
        'value': kv.value,
    }
```

Now, when we make assertions on our API endpoint's response, we can easily verify the integrity of the whole data. For list responses, though, it would be nice to pass a list of `KeyValue` instances and get a list of expressions back. For that, we have `pytest_drf.util.pluralized`:

```python
from pytest_drf.util import pluralized

express_key_values = pluralized(express_key_value)
```
```python
In [1]: a = KeyValue.objects.create(key='apples', value='oranges')

In [2]: b = KeyValue.objects.create(key='bananas', value='B A NA NA S')

In [3]: express_key_value(a)
Out[3]: {'id': 1, 'key': 'apples', 'value': 'oranges'}

In [4]: express_key_value(b)
Out[4]: {'id': 2, 'key': 'bananas', 'value': 'B A NA NA S'}

In [5]: express_key_values([a, b])
Out[5]:
[{'id': 1, 'key': 'apples', 'value': 'oranges'},
 {'id': 2, 'key': 'bananas', 'value': 'B A NA NA S'}]
```

Now that we're equipped, let's get to writing tests for each ViewSet action


## `TestList`

To verify the behavior of the list action, we want to check that it returns the proper structure for each `KeyValue` in the right order. So, let's actually create some `KeyValues` for our endpoint to respond with

```python
class TestList(
    UsesGetMethod,
    UsesListEndpoint,
    Returns200,
):
    key_values = lambda_fixture(
        lambda: [
            KeyValue.objects.create(key=key, value=value)
            for key, value in {
                'quay': 'worth',
                'chi': 'revenue',
                'umma': 'gumma',
            }.items()
        ],
        autouse=True,
    )
```

We use a dictionary to supply the information, and a list comprehension to create the actual rows. Note that we set `autouse=True`, so our `Returns200` test has a substantial response. If we didn't set it, the `Returns200` test wouldn't have any real rows — which might mask an exception in serialization.

And now let's verify the endpoint's response

```python
def test_it_returns_key_values(self, key_values, results):
    expected = express_key_values(sorted(key_values, key=lambda kv: kv.id))
    actual = results
    assert expected == actual
```

Here we use the `results` fixture, which is equivalent to `response.json()['results']` — it's where the actual API response is when using a pagination class. Our endpoint is using `PageNumberPagination`.

For our `expected` value, we lean on the pluralized version of our expression method. We pass it our source `KeyValue` instances, sorted by ID, because our `ViewSet` orders them the same.

Let's run the tests, and see how we're coming along

```bash
$ py.test --tb=no

tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_200 <- pytest_drf/status.py PASSED     [ 16%]
tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_key_values PASSED                      [ 33%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_201 <- pytest_drf/status.py FAILED   [ 50%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_200 <- pytest_drf/status.py ERROR  [ 66%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_returns_200 <- pytest_drf/status.py ERROR    [ 83%]
tests/test_kv.py::TestKeyValueViewSet::TestDestroy::test_it_returns_204 <- pytest_drf/status.py ERROR   [100%]
```

Ayyy, it passed! Making progress!


## `TestCreate`

When it comes to the "C" in "CRUD", there are a few behaviors the endpoint should and shouldn't have, if we're aiming to be thorough. Namely, the endpoint:

 - Should create a new `KeyValue`, and _only one_ `KeyValue` (and also shouldn't delete any others)
 - Should create a new `KeyValue` with precisely the data we POST
 - Should return the newly-created `KeyValue` in the proper structure

Before we get to those tests, let's setup our POST data, which is super simple:

```python
class TestCreate(
    UsesPostMethod,
    UsesListEndpoint,
    Returns201,
):
    data = static_fixture({
        'key': 'snakes',
        'value': 'hissssssss',
    })
```

We lean on [pytest-lambda](https://github.com/they4kman/pytest-lambda)'s `static_fixture`, which creates a fixture that returns a constant value. The `data` fixture will be POSTed as `client.post(data=data)`.

Now, to test whether the endpoint creates one and only one `KeyValue`, we must record which `KeyValue` rows exist _before_ the request, and compare them with the rows that exist _after_ the request. For this, we'll use `precondition_fixture`, a feature of [pytest-common-subject](https://github.com/theY4Kman/pytest-common-subject), which pytest-drf is built upon. Though the fixture performing each test's HTTP request is evaluated later than all others (using the `@pytest.mark.late` mark from [pytest-fixture-order](https://github.com/theY4Kman/pytest-fixture-order)), `precondition_fixture` uses pytest's dependency graph to 100% ensure it's evaluated before the request.

```python
from pytest_common_subject import precondition_fixture

initial_key_value_ids = precondition_fixture(
    lambda:
        set(KeyValue.objects.values_list('id', flat=True)))

def test_it_creates_new_key_value(self, initial_key_value_ids, json):
    expected = initial_key_value_ids | {json['id']}
    actual = set(KeyValue.objects.values_list('id', flat=True))
    assert expected == actual
```

So, we record a set of all the existing `KeyValue` IDs with our `precondition_fixture`. What we expect to see after the request is that only one new ID has been added: the ID of our newly-created `KeyValue`, which is returned in the API response. Let's check our test results now

```bash
$ py.test --tb=no

tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_200 <- pytest_drf/status.py PASSED     [ 14%]
tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_key_values PASSED                      [ 28%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_201 <- pytest_drf/status.py PASSED   [ 42%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_creates_new_key_value PASSED                 [ 57%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_200 <- pytest_drf/status.py ERROR  [ 71%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_returns_200 <- pytest_drf/status.py ERROR    [ 85%]
tests/test_kv.py::TestKeyValueViewSet::TestDestroy::test_it_returns_204 <- pytest_drf/status.py ERROR   [100%]
```

Success!

Next up is verifying that the newly-created `KeyValue` has exactly the field values we POSTed.

```python
from pytest_assert_utils import assert_model_attrs

def test_it_sets_expected_attrs(self, data, json):
    key_value = KeyValue.objects.get(pk=json['id'])

    expected = data
    assert_model_attrs(key_value, expected)
```

Here we lean on `assert_model_attrs` from [pytest-assert-utils](https://github.com/theY4Kman/pytest-assert-utils), which performs a dict-to-dict comparison under the hood, so if the items aren't equal, pytest will display a diff. Let's run it

```bash
$ py.test --tb=no

tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_200 <- pytest_drf/status.py PASSED     [ 12%]
tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_key_values PASSED                      [ 25%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_201 <- pytest_drf/status.py PASSED   [ 37%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_creates_new_key_value PASSED                 [ 50%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_sets_expected_attrs PASSED                   [ 62%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_200 <- pytest_drf/status.py ERROR  [ 75%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_returns_200 <- pytest_drf/status.py ERROR    [ 87%]
tests/test_kv.py::TestKeyValueViewSet::TestDestroy::test_it_returns_204 <- pytest_drf/status.py ERROR   [100%]
```

Nice!

Last but not least, we verify the structure of the API response. 

```python
def test_it_returns_key_value(self, json):
    key_value = KeyValue.objects.get(pk=json['id'])

    expected = express_key_value(key_value)
    actual = json
    assert expected == actual
```

```bash
$ py.test --tb=no

tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_200 <- pytest_drf/status.py PASSED     [ 11%]
tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_key_values PASSED                      [ 22%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_201 <- pytest_drf/status.py PASSED   [ 33%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_creates_new_key_value PASSED                 [ 44%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_sets_expected_attrs PASSED                   [ 55%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_key_value PASSED                     [ 66%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_200 <- pytest_drf/status.py ERROR  [ 77%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_returns_200 <- pytest_drf/status.py ERROR    [ 88%]
tests/test_kv.py::TestKeyValueViewSet::TestDestroy::test_it_returns_204 <- pytest_drf/status.py ERROR   [100%]
```

Yay! Our create action is covered!


## `TestRetrieve`

Retrieval is simple to test: just create a `KeyValue` beforehand, and verify the endpoint returns it in the proper structure. It's also the first of the ViewSet actions to use the `detail_url`. We're gonna define the `key_value` fixture that `detail_url` requests

```python
class TestRetrieve(
    UsesGetMethod,
    UsesDetailEndpoint,
    Returns200,
):
    key_value = lambda_fixture(
        lambda:
            KeyValue.objects.create(
                key='monty',
                value='jython',
            ))
```

And with our expression method, verifying the API response is a cinch

```python
def test_it_returns_key_value(self, key_value, json):
    expected = express_key_value(key_value)
    actual = json
    assert expected == actual
```

```bash
$ py.test --tb=no

tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_200 <- pytest_drf/status.py PASSED     [ 10%]
tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_key_values PASSED                      [ 20%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_201 <- pytest_drf/status.py PASSED   [ 30%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_creates_new_key_value PASSED                 [ 40%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_sets_expected_attrs PASSED                   [ 50%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_key_value PASSED                     [ 60%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_200 <- pytest_drf/status.py PASSED [ 70%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_key_value PASSED                   [ 80%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_returns_200 <- pytest_drf/status.py ERROR    [ 90%]
tests/test_kv.py::TestKeyValueViewSet::TestDestroy::test_it_returns_204 <- pytest_drf/status.py ERROR   [100%]
```

Almost done!


## `TestUpdate`

The update endpoint should do two things:

 - Change the `KeyValue` row in the database to match _precisely_ what we've POSTed
 - Return the updated `KeyValue` in the proper structure

Like our retrieve tests, we'll start by defining the `key_value` fixture, which we'll be updating through our request; but we'll also declare the data we'll be POSTing

```python
class TestUpdate(
    UsesPatchMethod,
    UsesDetailEndpoint,
    Returns200,
):
    key_value = lambda_fixture(
        lambda:
            KeyValue.objects.create(
                key='pipenv',
                value='was a huge leap forward',
            ))

    data = static_fixture({
        'key': 'buuut poetry',
        'value': 'locks quicker and i like that',
    })
```

So let's test that our POSTed data makes it to the database

```python
def test_it_sets_expected_attrs(self, data, key_value):
    # We must tell Django to grab fresh data from the database, or we'll
    # see our stale initial data and think our endpoint is broken!
    key_value.refresh_from_db()

    expected = data
    assert_model_attrs(key_value, expected)
```

```bash
$ py.test --tb=no

tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_200 <- pytest_drf/status.py PASSED     [  9%]
tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_key_values PASSED                      [ 18%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_201 <- pytest_drf/status.py PASSED   [ 27%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_creates_new_key_value PASSED                 [ 36%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_sets_expected_attrs PASSED                   [ 45%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_key_value PASSED                     [ 54%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_200 <- pytest_drf/status.py PASSED [ 63%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_key_value PASSED                   [ 72%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_returns_200 <- pytest_drf/status.py PASSED   [ 81%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_sets_expected_attrs PASSED                   [ 90%]
tests/test_kv.py::TestKeyValueViewSet::TestDestroy::test_it_returns_204 <- pytest_drf/status.py ERROR   [100%]
```

Excellent.

Now just the standard response structure verification, though this time we'll have to do the same `refresh_from_db()` dance as the last test, for the same reason

```python
def test_it_returns_key_value(self, key_value, json):
    key_value.refresh_from_db()

    expected = express_key_value(key_value)
    actual = json
    assert expected == actual
```

```bash
$ py.test --tb=no

tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_200 <- pytest_drf/status.py PASSED     [  8%]
tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_key_values PASSED                      [ 16%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_201 <- pytest_drf/status.py PASSED   [ 25%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_creates_new_key_value PASSED                 [ 33%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_sets_expected_attrs PASSED                   [ 41%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_key_value PASSED                     [ 50%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_200 <- pytest_drf/status.py PASSED [ 58%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_key_value PASSED                   [ 66%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_returns_200 <- pytest_drf/status.py PASSED   [ 75%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_sets_expected_attrs PASSED                   [ 83%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_returns_key_value PASSED                     [ 91%]
tests/test_kv.py::TestKeyValueViewSet::TestDestroy::test_it_returns_204 <- pytest_drf/status.py ERROR   [100%]
```

Boom! Just the destroy action left!


## `TestDestroy`

Last but not least (well, maybe in terms of `KeyValue.objects.count()`), we have our deletion endpoint. Its only behavior is to delete the specified `KeyValue`, and _only_ the specified `KeyValue`. Similar to `TestCreate`, we'll use a `precondition_fixture` to record the initial set of `KeyValue` IDs — though, this time we'll include the `KeyValue` we'll be deleting in the list

```python
class TestDestroy(
    UsesDeleteMethod,
    UsesDetailEndpoint,
    Returns204,
):
    key_value = lambda_fixture(
        lambda:
            KeyValue.objects.create(
                key='i love',
                value='YOU',
            ))

    initial_key_value_ids = precondition_fixture(
        lambda key_value:  # ensure our to-be-deleted KeyValue exists in our set
            set(KeyValue.objects.values_list('id', flat=True)))

    def test_it_deletes_key_value(self, initial_key_value_ids, key_value):
        expected = initial_key_value_ids - {key_value.id}
        actual = set(KeyValue.objects.values_list('id', flat=True))
        assert expected == actual
```

```bash
$ py.test --tb=no

tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_200 <- pytest_drf/status.py PASSED     [  7%]
tests/test_kv.py::TestKeyValueViewSet::TestList::test_it_returns_key_values PASSED                      [ 15%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_201 <- pytest_drf/status.py PASSED   [ 23%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_creates_new_key_value PASSED                 [ 30%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_sets_expected_attrs PASSED                   [ 38%]
tests/test_kv.py::TestKeyValueViewSet::TestCreate::test_it_returns_key_value PASSED                     [ 46%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_200 <- pytest_drf/status.py PASSED [ 53%]
tests/test_kv.py::TestKeyValueViewSet::TestRetrieve::test_it_returns_key_value PASSED                   [ 61%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_returns_200 <- pytest_drf/status.py PASSED   [ 69%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_sets_expected_attrs PASSED                   [ 76%]
tests/test_kv.py::TestKeyValueViewSet::TestUpdate::test_it_returns_key_value PASSED                     [ 84%]
tests/test_kv.py::TestKeyValueViewSet::TestDestroy::test_it_returns_204 <- pytest_drf/status.py PASSED  [ 92%]
tests/test_kv.py::TestKeyValueViewSet::TestDestroy::test_it_deletes_key_value PASSED                    [100%]

============================================= 13 passed in 0.42s ==============================================
```

Yaaaaay!


## Putting it all together

```python
# tests/test_kv.py

from typing import Any, Dict

from pytest_common_subject import precondition_fixture
from pytest_drf import (
    ViewSetTest,
    Returns200,
    Returns201,
    Returns204,
    UsesGetMethod,
    UsesDeleteMethod,
    UsesDetailEndpoint,
    UsesListEndpoint,
    UsesPatchMethod,
    UsesPostMethod,
)
from pytest_drf.util import pluralized, url_for
from pytest_lambda import lambda_fixture, static_fixture
from pytest_assert_utils import assert_model_attrs


def express_key_value(kv: KeyValue) -> Dict[str, Any]:
    return {
        'id': kv.id,
        'key': kv.key,
        'value': kv.value,
    }

express_key_values = pluralized(express_key_value)


class TestKeyValueViewSet(ViewSetTest):
    list_url = lambda_fixture(
        lambda:
            url_for('key-values-list'))

    detail_url = lambda_fixture(
        lambda key_value:
            url_for('key-values-detail', key_value.pk))

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        key_values = lambda_fixture(
            lambda: [
                KeyValue.objects.create(key=key, value=value)
                for key, value in {
                    'quay': 'worth',
                    'chi': 'revenue',
                    'umma': 'gumma',
                }.items()
            ],
            autouse=True,
        )

        def test_it_returns_key_values(self, key_values, results):
            expected = express_key_values(sorted(key_values, key=lambda kv: kv.id))
            actual = results
            assert expected == actual

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        data = static_fixture({
            'key': 'snakes',
            'value': 'hissssssss',
        })

        initial_key_value_ids = precondition_fixture(
            lambda:
                set(KeyValue.objects.values_list('id', flat=True)))

        def test_it_creates_new_key_value(self, initial_key_value_ids, json):
            expected = initial_key_value_ids | {json['id']}
            actual = set(KeyValue.objects.values_list('id', flat=True))
            assert expected == actual

        def test_it_sets_expected_attrs(self, data, json):
            key_value = KeyValue.objects.get(pk=json['id'])

            expected = data
            assert_model_attrs(key_value, expected)

        def test_it_returns_key_value(self, json):
            key_value = KeyValue.objects.get(pk=json['id'])

            expected = express_key_value(key_value)
            actual = json
            assert expected == actual


    class TestRetrieve(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        key_value = lambda_fixture(
            lambda:
                KeyValue.objects.create(
                    key='monty',
                    value='jython',
                ))

        def test_it_returns_key_value(self, key_value, json):
            expected = express_key_value(key_value)
            actual = json
            assert expected == actual

    class TestUpdate(
        UsesPatchMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        key_value = lambda_fixture(
            lambda:
                KeyValue.objects.create(
                    key='pipenv',
                    value='was a huge leap forward',
                ))

        data = static_fixture({
            'key': 'buuut poetry',
            'value': 'locks quicker and i like that',
        })

        def test_it_sets_expected_attrs(self, data, key_value):
            # We must tell Django to grab fresh data from the database, or we'll
            # see our stale initial data and think our endpoint is broken!
            key_value.refresh_from_db()

            expected = data
            assert_model_attrs(key_value, expected)

        def test_it_returns_key_value(self, key_value, json):
            key_value.refresh_from_db()

            expected = express_key_value(key_value)
            actual = json
            assert expected == actual

    class TestDestroy(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        Returns204,
    ):
        key_value = lambda_fixture(
            lambda:
                KeyValue.objects.create(
                    key='i love',
                    value='YOU',
                ))

        initial_key_value_ids = precondition_fixture(
            lambda key_value:  # ensure our to-be-deleted KeyValue exists in our set
                set(KeyValue.objects.values_list('id', flat=True)))

        def test_it_deletes_key_value(self, initial_key_value_ids, key_value):
            expected = initial_key_value_ids - {key_value.id}
            actual = set(KeyValue.objects.values_list('id', flat=True))
            assert expected == actual
```

It's quite a feat!

Now, we tested an already-existing endpoint here, just for demonstration purposes. But there's a bigger advantage to performing one request per test, and having a single responsibility for each test: we can write the tests first and incrementally build the ViewSet. We run the tests on changes, and when they're all green, we know the endpoint is done.

The beauty of the tests-first methodology is that it frees us up to be creative. Because we have a definite end condition, we can experiment with better implementations — more maintainable, easier to read, using best practices, perhaps leaning on a third-party package for heavy lifting.

Well, congratulations if you've made it this far. I hope you may find some value in this library, or even from some conventions in these example tests. Good luck out there, and remember: readability counts — in tests, doubly so.


## Bonus: BDD syntax

Personally, I like to use `DescribeKeyValueViewSet`, and `DescribeList`, `DescribeCreate`, etc for my test classes. If I'm testing `DescribeCreate` as a particular user, I like to use, e.g., `ContextAsAdmin`. Sometimes `CaseUnauthenticated` hits the spot.

And for test methods, I love to omit the `test` in `test_it_does_xyz`, and simply put `it_does_xyz`.

To appease my leanings toward BDD namings, I use a `pytest.ini` with these options:

```ini
[pytest]
# Only search for tests within files matching these patterns
python_files = tests.py test_*.py

# Discover tests within classes matching these patterns
# NOTE: the dash represents a word boundary (functionality provided by pytest-camel-collect)
python_classes = Test-* Describe-* Context-* With-* Without-* For-* When-* If-* Case-*

# Only methods matching these patterns are considered tests
python_functions = test_* it_* its_*
```

About the dashes in `python_classes`: sometimes I'll name a test class `ForAdminUsers`. If I had the pattern `For*`, it would also match a pytest-drf mixin named `ForbidsAnonymousUsers`. [pytest-camel-collect](https://github.com/theY4Kman/pytest-camel-collect) is a little plugin that interprets dashes in `python_classes` as CamelCase word boundaries. However, similar behavior can be had on stock pytest using a pattern like `For[A-Z0-9]*`.

Here's what our example `KeyValueViewSet` test would look like with this BDD naming scheme

<details>
<summary>BDD-esque KeyValueViewSet test</summary>

```python
from typing import Any, Dict

from pytest_common_subject import precondition_fixture
from pytest_drf import (
    ViewSetTest,
    Returns200,
    Returns201,
    Returns204,
    UsesGetMethod,
    UsesDeleteMethod,
    UsesDetailEndpoint,
    UsesListEndpoint,
    UsesPatchMethod,
    UsesPostMethod,
)
from pytest_drf.util import pluralized, url_for
from pytest_lambda import lambda_fixture, static_fixture
from pytest_assert_utils import assert_model_attrs


def express_key_value(kv: KeyValue) -> Dict[str, Any]:
    return {
        'id': kv.id,
        'key': kv.key,
        'value': kv.value,
    }

express_key_values = pluralized(express_key_value)


class DescribeKeyValueViewSet(ViewSetTest):
    list_url = lambda_fixture(
        lambda:
            url_for('key-values-list'))

    detail_url = lambda_fixture(
        lambda key_value:
            url_for('key-values-detail', key_value.pk))

    class DescribeList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        key_values = lambda_fixture(
            lambda: [
                KeyValue.objects.create(key=key, value=value)
                for key, value in {
                    'quay': 'worth',
                    'chi': 'revenue',
                    'umma': 'gumma',
                }.items()
            ],
            autouse=True,
        )

        def it_returns_key_values(self, key_values, results):
            expected = express_key_values(sorted(key_values, key=lambda kv: kv.id))
            actual = results
            assert expected == actual

    class DescribeCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        data = static_fixture({
            'key': 'snakes',
            'value': 'hissssssss',
        })

        initial_key_value_ids = precondition_fixture(
            lambda:
                set(KeyValue.objects.values_list('id', flat=True)))

        def it_creates_new_key_value(self, initial_key_value_ids, json):
            expected = initial_key_value_ids | {json['id']}
            actual = set(KeyValue.objects.values_list('id', flat=True))
            assert expected == actual

        def it_sets_expected_attrs(self, data, json):
            key_value = KeyValue.objects.get(pk=json['id'])

            expected = data
            assert_model_attrs(key_value, expected)

        def it_returns_key_value(self, json):
            key_value = KeyValue.objects.get(pk=json['id'])

            expected = express_key_value(key_value)
            actual = json
            assert expected == actual


    class DescribeRetrieve(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        key_value = lambda_fixture(
            lambda:
                KeyValue.objects.create(
                    key='monty',
                    value='jython',
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
        key_value = lambda_fixture(
            lambda:
                KeyValue.objects.create(
                    key='pipenv',
                    value='was a huge leap forward',
                ))

        data = static_fixture({
            'key': 'buuut poetry',
            'value': 'locks quicker and i like that',
        })

        def it_sets_expected_attrs(self, data, key_value):
            # We must tell Django to grab fresh data from the database, or we'll
            # see our stale initial data and think our endpoint is broken!
            key_value.refresh_from_db()

            expected = data
            assert_model_attrs(key_value, expected)

        def it_returns_key_value(self, key_value, json):
            key_value.refresh_from_db()

            expected = express_key_value(key_value)
            actual = json
            assert expected == actual

    class DescribeDestroy(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        Returns204,
    ):
        key_value = lambda_fixture(
            lambda:
                KeyValue.objects.create(
                    key='i love',
                    value='YOU',
                ))

        initial_key_value_ids = precondition_fixture(
            lambda key_value:  # ensure our to-be-deleted KeyValue exists in our set
                set(KeyValue.objects.values_list('id', flat=True)))

        def it_deletes_key_value(self, initial_key_value_ids, key_value):
            expected = initial_key_value_ids - {key_value.id}
            actual = set(KeyValue.objects.values_list('id', flat=True))
            assert expected == actual
```

</details>
