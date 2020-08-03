from django.contrib.auth.models import User
from django.urls import reverse

from pytest_lambda import lambda_fixture

from pytest_drf import APIViewTest, AsUser, UsesGetMethod


alice = lambda_fixture(lambda db: User.objects.create(
    username='alice',
    first_name='Alice',
    last_name='Innchains',
    email='alice@ali.ce',
))

bob = lambda_fixture(lambda db: User.objects.create(
    username='bob',
    first_name='Bob',
    last_name='Loblaw',
    email='bob@lobl.aw',
))


class DescribeUserInfo(
    APIViewTest,
    UsesGetMethod,
):
    # NOTE: this view returns the username, first_name, last_name, and email of
    #       the authenticated user.
    url = lambda_fixture(lambda: reverse('authentication-user-info'))


    class CaseAlice(AsUser('alice')):
        def it_returns_alices_info(self, alice, json):
            expected = {
                'username': alice.username,
                'first_name': alice.first_name,
                'last_name': alice.last_name,
                'email': alice.email,
            }
            actual = json
            assert expected == actual


    class CaseBob(AsUser('bob')):
        def it_returns_bobs_info(self, bob, json):
            expected = {
                'username': bob.username,
                'first_name': bob.first_name,
                'last_name': bob.last_name,
                'email': bob.email,
            }
            actual = json
            assert expected == actual


    class CaseAnonymous:
        def it_returns_no_info(self, json):
            # NOTE: AnonymousUser does not define first_name, last_name, or email.
            expected = {'username': ''}
            actual = json
            assert expected == actual
