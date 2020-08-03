from django.urls import reverse
from pytest_lambda import lambda_fixture, not_implemented_fixture, static_fixture

from pytest_drf import (
    APIViewTest,
    Returns200,
    Returns201,
    Returns202,
    Returns204,
    Returns301,
    Returns302,
    Returns304,
    Returns307,
    Returns308,
    Returns400,
    Returns401,
    Returns403,
    Returns404,
    Returns405,
    Returns409,
    Returns422,
    Returns429,
    Returns500,
    Returns503,
    Returns504,
    ReturnsStatus,
    UsesGetMethod,
)


class DescribeStatusCode(
    APIViewTest,
    UsesGetMethod,
):
    # Status code to be returned from view.
    # This will be overridden in child test contexts.
    status_code = not_implemented_fixture()

    url = lambda_fixture(
        lambda status_code:
            reverse('status-code', kwargs={'code': status_code}))


    class Case200(Returns200):
        status_code = static_fixture(200)

    class Case201(Returns201):
        status_code = static_fixture(201)

    class Case202(Returns202):
        status_code = static_fixture(202)

    class Case204(Returns204):
        status_code = static_fixture(204)

    class Case301(Returns301):
        status_code = static_fixture(301)

    class Case302(Returns302):
        status_code = static_fixture(302)

    class Case304(Returns304):
        status_code = static_fixture(304)

    class Case307(Returns307):
        status_code = static_fixture(307)

    class Case308(Returns308):
        status_code = static_fixture(308)

    class Case400(Returns400):
        status_code = static_fixture(400)

    class Case401(Returns401):
        status_code = static_fixture(401)

    class Case403(Returns403):
        status_code = static_fixture(403)

    class Case404(Returns404):
        status_code = static_fixture(404)

    class Case405(Returns405):
        status_code = static_fixture(405)

    class Case409(Returns409):
        status_code = static_fixture(409)

    class Case422(Returns422):
        status_code = static_fixture(422)

    class Case429(Returns429):
        status_code = static_fixture(429)

    class Case500(Returns500):
        status_code = static_fixture(500)

    class Case503(Returns503):
        status_code = static_fixture(503)

    class Case504(Returns504):
        status_code = static_fixture(504)

    class CaseArbitrary(ReturnsStatus(599)):
        status_code = static_fixture(599)
