from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url, user, status',
    (
        (
            pytest.lazy_fixture('NEWS_HOME'),
            pytest.lazy_fixture('client_anonymous'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('USERS_LOGIN'),
            pytest.lazy_fixture('client_anonymous'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('USERS_LOGOUT'),
            pytest.lazy_fixture('client_anonymous'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('USERS_SIGNUP'),
            pytest.lazy_fixture('client_anonymous'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('NEWS_DETAIL'),
            pytest.lazy_fixture('client_anonymous'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('COMMENT_EDIT'),
            pytest.lazy_fixture('client_author'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('COMMENT_DELETE'),
            pytest.lazy_fixture('client_author'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('COMMENT_EDIT'),
            pytest.lazy_fixture('client_reader'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('COMMENT_DELETE'),
            pytest.lazy_fixture('client_reader'),
            HTTPStatus.NOT_FOUND
        ),
    )
)
def test_pages_availability_for_users(url, user, status):
    # Act
    response = user.get(url)

    assert response.status_code == status


@pytest.mark.parametrize(
    'url, user, redirect',
    (
        (
            pytest.lazy_fixture('COMMENT_EDIT'),
            pytest.lazy_fixture('client_anonymous'),
            pytest.lazy_fixture('USERS_LOGIN')
        ),
        (
            pytest.lazy_fixture('COMMENT_DELETE'),
            pytest.lazy_fixture('client_anonymous'),
            pytest.lazy_fixture('USERS_LOGIN')
        ),
    )
)
def test_pages_no_availability_for_anonymous_user(url, user, redirect):
    expected_url = f'{redirect}?next={url}'

    # Act
    response = user.get(url)

    assertRedirects(response, expected_url)
