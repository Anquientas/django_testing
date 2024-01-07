from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
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


User = get_user_model()


class TestRoutes(TestCase):

    NOTE_SLUG = 'Slug'

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
            slug=cls.SLUG,
            author=cls.author,
        )

    def test_pages_availability_for_users(self):
        urls_client_statuses = (
            (NOTES_HOME, None, self.anonymous_client, HTTPStatus.OK),
            (USERS_LOGIN, None, self.anonymous_client, HTTPStatus.OK),
            (USERS_LOGOUT, None, self.anonymous_client, HTTPStatus.OK),
            (USERS_SIGNUP, None, self.anonymous_client, HTTPStatus.OK),
            (NOTES_ADD, None, self.reader_client, HTTPStatus.OK),
            (NOTES_LIST, None, self.reader_client, HTTPStatus.OK),
            (NOTES_SUCCESS, None, self.reader_client, HTTPStatus.OK),
            (
                NOTES_EDIT,
                (self.NOTE_SLUG,),
                self.author_client,
                HTTPStatus.OK
            ),
            (
                NOTES_DELETE,
                (self.NOTE_SLUG,),
                self.author_client,
                HTTPStatus.OK
            ),
            (
                NOTES_DETAIL,
                (self.NOTE_SLUG,),
                self.author_client,
                HTTPStatus.OK
            ),
            (
                NOTES_EDIT,
                (self.NOTE_SLUG,),
                self.reader_client,
                HTTPStatus.NOT_FOUND
            ),
            (
                NOTES_DELETE,
                (self.NOTE_SLUG,),
                self.reader_client,
                HTTPStatus.NOT_FOUND
            ),
            (
                NOTES_DETAIL,
                (self.NOTE_SLUG,),
                self.reader_client,
                HTTPStatus.NOT_FOUND
            ),
        )

        for name, args, user, status in urls_client_statuses:
            # print(user.get(user))
            with self.subTest(name=name, user=user, expected_result=status):
                url = reverse(name, args=args)
                self.assertEqual(user.get(url).status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse(USERS_LOGIN)
        urls = (
            (NOTES_ADD, None),
            (NOTES_LIST, None),
            (NOTES_SUCCESS, None),
            (NOTES_EDIT, (self.SLUG,)),
            (NOTES_DELETE, (self.SLUG,)),
            (NOTES_DETAIL, (self.SLUG,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.assertRedirects(
                    self.client.get(url),
                    f'{login_url}?next={url}'
                )
