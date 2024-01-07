from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note
from .urls import (
    NOTE_SLUG,
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


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='У. Черчиль')
        cls.author_client = Client()
        cls.author_client.force_login(user=cls.author)

        cls.reader = User.objects.create(username='Читатель заметки')
        cls.reader_client = Client()
        cls.reader_client.force_login(user=cls.reader)

        cls.anonymous_client = Client()

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=NOTE_SLUG,
            author=cls.author,
        )

    def test_pages_availability_for_users(self):
        urls_client_statuses = (
            (NOTES_HOME, self.anonymous_client, HTTPStatus.OK),
            (USERS_LOGIN, self.anonymous_client, HTTPStatus.OK),
            (USERS_LOGOUT, self.anonymous_client, HTTPStatus.OK),
            (USERS_SIGNUP, self.anonymous_client, HTTPStatus.OK),
            (NOTES_ADD, self.reader_client, HTTPStatus.OK),
            (NOTES_LIST, self.reader_client, HTTPStatus.OK),
            (NOTES_SUCCESS, self.reader_client, HTTPStatus.OK),
            (NOTES_EDIT, self.author_client, HTTPStatus.OK),
            (NOTES_DELETE, self.author_client, HTTPStatus.OK),
            (NOTES_DETAIL, self.author_client, HTTPStatus.OK),
            (NOTES_EDIT, self.reader_client, HTTPStatus.NOT_FOUND),
            (NOTES_DELETE, self.reader_client, HTTPStatus.NOT_FOUND),
            (NOTES_DETAIL, self.reader_client, HTTPStatus.NOT_FOUND),
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
                    self.anonymous_client.get(url),
                    f'{USERS_LOGIN}?next={url}'
                )
