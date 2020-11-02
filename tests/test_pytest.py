from _pytest.python import _showfixtures_main


def test_pytest_fixtures(request):
    """Running `py.test --fixtures` should not fail
    """
    try:
        _showfixtures_main(request.config, request.session)
    except Exception as e:
        raise AssertionError(f'Error showing fixtures: {e}')
