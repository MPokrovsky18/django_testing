from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_constant, parametrized_client, expected_status',
    (
        (
            pytest.lazy_fixture('home_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('news_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('login_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('logout_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('signup_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('admin_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('admin_client'),
            HTTPStatus.NOT_FOUND
        ),
    )
)
def test_pages_availability_for_difference_users(
    url_constant, parametrized_client, expected_status
):
    """Check the availability of pages for difference users."""
    response = parametrized_client.get(url_constant)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_constant',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url')
    )
)
def test_redirect_for_anonymous_client(client, url_constant, login_url):
    """Check redirection for an anonymous client."""
    expexted_url = f'{login_url}?next={url_constant}'
    response = client.get(url_constant)
    assertRedirects(response, expexted_url)
