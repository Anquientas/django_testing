from http import HTTPStatus

from django.test import Client

from .overall import Overall
from .urls import (
    NOTES_ADD,
    NOTES_DELETE,
    NOTES_DETAIL,
    NOTES_EDIT,
    NOTES_HOME,
    NOTES_LIST,
    NOTES_SUCCESS,
    USERS_LOGIN,
    USERS_LOGOUT,
    USERS_SIGNUP
)


class TestRoutes(Overall):

    @classmethod
    def setUpTestData(cls):
        Overall.setUpTestData()
        cls.client_anonymous = Client()

    def test_pages_availability_for_users(self):
        urls_client_statuses = (
            (NOTES_HOME, self.client_anonymous, HTTPStatus.OK),
            (USERS_LOGIN, self.client_anonymous, HTTPStatus.OK),
            (USERS_LOGOUT, self.client_anonymous, HTTPStatus.OK),
            (USERS_SIGNUP, self.client_anonymous, HTTPStatus.OK),
            (NOTES_ADD, self.client_reader, HTTPStatus.OK),
            (NOTES_LIST, self.client_reader, HTTPStatus.OK),
            (NOTES_SUCCESS, self.client_reader, HTTPStatus.OK),
            (NOTES_EDIT, self.client_author, HTTPStatus.OK),
            (NOTES_DELETE, self.client_author, HTTPStatus.OK),
            (NOTES_DETAIL, self.client_author, HTTPStatus.OK),
            (NOTES_EDIT, self.client_reader, HTTPStatus.NOT_FOUND),
            (NOTES_DELETE, self.client_reader, HTTPStatus.NOT_FOUND),
            (NOTES_DETAIL, self.client_reader, HTTPStatus.NOT_FOUND),
        )

        for url, user, status in urls_client_statuses:
            with self.subTest(url=url, user=user, expected_result=status):
                self.assertEqual(user.get(url).status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            NOTES_ADD,
            NOTES_LIST,
            NOTES_SUCCESS,
            NOTES_EDIT,
            NOTES_DELETE,
            NOTES_DETAIL,
        )
        for url in urls:
            with self.subTest(url=url, expected_result=USERS_LOGIN):
                self.assertRedirects(
                    self.client_anonymous.get(url),
                    f'{USERS_LOGIN}?next={url}'
                )
