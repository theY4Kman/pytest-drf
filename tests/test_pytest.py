from copy import copy

from _pytest.python import _showfixtures_main


def test_pytest_fixtures(request):
    """Running `py.test --fixtures` should not fail
    """
    #
    # Use a copy of the session, so as not to interfere with collection stats.
    #
    # If the actual session are is used, pytest will exit with code 5:
    # no tests collected. This causes the Travis build to be marked as failed.
    #
    session = copy(request.session)

    try:
        _showfixtures_main(request.config, session)
    except Exception as e:
        raise AssertionError(f'Error showing fixtures: {e}')
