from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


COMMENT_DELETE = pytest.lazy_fixture('comment_delete_url')
COMMENT_EDIT = pytest.lazy_fixture('comment_edit_url')
NEWS_DETAIL = pytest.lazy_fixture('news_detail_url')
NEWS_HOME = pytest.lazy_fixture('news_home_url')

USERS_LOGIN = pytest.lazy_fixture('users_login_url')
USERS_LOGOUT = pytest.lazy_fixture('users_logout_url')
USERS_SIGNUP = pytest.lazy_fixture('users_signup_url')

CLIENT_ANONYMOUS = pytest.lazy_fixture('client')
CLIENT_AUTHOR = pytest.lazy_fixture('client_author')
CLIENT_READER = pytest.lazy_fixture('client_reader')


@pytest.mark.parametrize(
    'url, client_user, status',
    (
        (NEWS_HOME, CLIENT_ANONYMOUS, HTTPStatus.OK),
        (USERS_LOGIN, CLIENT_ANONYMOUS, HTTPStatus.OK),
        (USERS_LOGOUT, CLIENT_ANONYMOUS, HTTPStatus.OK),
        (USERS_SIGNUP, CLIENT_ANONYMOUS, HTTPStatus.OK),
        (NEWS_DETAIL, CLIENT_ANONYMOUS, HTTPStatus.OK),
        (COMMENT_EDIT, CLIENT_AUTHOR, HTTPStatus.OK),
        (COMMENT_DELETE, CLIENT_AUTHOR, HTTPStatus.OK),
        (COMMENT_EDIT, CLIENT_READER, HTTPStatus.NOT_FOUND),
        (COMMENT_DELETE, CLIENT_READER, HTTPStatus.NOT_FOUND),
    )
)
def test_pages_availability_for_users(url, client_user, status):
    assert client_user.get(url).status_code == status


@pytest.mark.parametrize(
    'url, client_user, redirect',
    (
        (COMMENT_EDIT, CLIENT_ANONYMOUS, USERS_LOGIN),
        (COMMENT_DELETE, CLIENT_ANONYMOUS, USERS_LOGIN),
    )
)
def test_pages_no_availability_for_anonymous_user(url,
                                                  client_user,
                                                  redirect,
                                                  expected_url):
    assertRedirects(
        client_user.get(url),
        expected_url.format(redirect=redirect, url=url)
    )
