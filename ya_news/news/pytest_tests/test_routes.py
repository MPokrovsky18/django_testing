from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


HOME_URL = pytest.lazy_fixture('home_url')
NEWS_URL = pytest.lazy_fixture('news_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
CLIENT = pytest.lazy_fixture('client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
ADMIN_CLIENT = pytest.lazy_fixture('admin_client')


@pytest.mark.parametrize(
    'url_constant, parametrized_client, expected_status',
    (
        (HOME_URL, CLIENT, HTTPStatus.OK),
        (NEWS_URL, CLIENT, HTTPStatus.OK),
        (LOGIN_URL, CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, CLIENT, HTTPStatus.OK),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, ADMIN_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_URL, ADMIN_CLIENT, HTTPStatus.NOT_FOUND),
    )
)
def test_pages_availability_for_difference_users(
    url_constant, parametrized_client, expected_status
):
    """Check the availability of pages for difference users."""
    assert parametrized_client.get(url_constant).status_code == expected_status


@pytest.mark.parametrize(
    'url_constant',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url')
    )
)
def test_redirect_for_anonymous_client(client, url_constant, login_url):
    """Check redirection for an anonymous client."""
    assertRedirects(
        client.get(url_constant), f'{login_url}?next={url_constant}'
    )
