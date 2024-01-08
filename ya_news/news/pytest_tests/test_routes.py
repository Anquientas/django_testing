from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


COMMENT_DELETE = pytest.lazy_fixture('comment_delete')
COMMENT_EDIT = pytest.lazy_fixture('comment_edit')
NEWS_DETAIL = pytest.lazy_fixture('news_detail')
NEWS_HOME = pytest.lazy_fixture('news_home')
USERS_LOGIN = pytest.lazy_fixture('users_login')
USERS_LOGOUT = pytest.lazy_fixture('users_logout')
USERS_SIGNUP = pytest.lazy_fixture('users_signup')


@pytest.mark.parametrize(
    'url, user, status',
    (
        (
            NEWS_HOME,
            pytest.lazy_fixture('client_anonymous'),
            HTTPStatus.OK
        ),
        (
            USERS_LOGIN,
            pytest.lazy_fixture('client_anonymous'),
            HTTPStatus.OK
        ),
        (
            USERS_LOGOUT,
            pytest.lazy_fixture('client_anonymous'),
            HTTPStatus.OK
        ),
        (
            USERS_SIGNUP,
            pytest.lazy_fixture('client_anonymous'),
            HTTPStatus.OK
        ),
        (
            NEWS_DETAIL,
            pytest.lazy_fixture('client_anonymous'),
            HTTPStatus.OK
        ),
        (
            COMMENT_EDIT,
            pytest.lazy_fixture('client_author'),
            HTTPStatus.OK
        ),
        (
            COMMENT_DELETE,
            pytest.lazy_fixture('client_author'),
            HTTPStatus.OK
        ),
        (
            COMMENT_EDIT,
            pytest.lazy_fixture('client_reader'),
            HTTPStatus.NOT_FOUND
        ),
        (
            COMMENT_DELETE,
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
            COMMENT_EDIT,
            pytest.lazy_fixture('client_anonymous'),
            USERS_LOGIN
        ),
        (
            COMMENT_DELETE,
            pytest.lazy_fixture('client_anonymous'),
            USERS_LOGIN
        ),
    )
)
def test_pages_no_availability_for_anonymous_user(url, user, redirect):
    expected_url = f'{redirect}?next={url}'

    # Act
    response = user.get(url)

    assertRedirects(response, expected_url)
