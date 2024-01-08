from http import HTTPStatus

from pytils.translit import slugify
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note
from notes.forms import WARNING
from .urls import (
    NOTE_SLUG,
    NOTES_ADD,
    NOTES_DELETE,
    NOTES_EDIT,
    NOTES_SUCCESS,
)


User = get_user_model()


class GlobalClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='У. Черчиль')
        cls.client_author = Client()
        cls.client_author.force_login(user=cls.author)

        cls.user = User.objects.create(username='Читатель заметки')
        cls.client_user = Client()
        cls.client_user.force_login(user=cls.user)

        cls.anonymous_client = Client()

        cls.note = Note.objects.create(
            title='Заголовок INITIAL',
            text='Просто текст INITIAL.',
            slug=NOTE_SLUG,
            author=cls.author,
        )

        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Просто текст.',
            'slug': 'Slug_1',
        }

        cls.form_new_data = {
            'title': 'Новый заголовок',
            'text': 'Просто новый текст.',
            'slug': 'New_slug',
        }

        cls.form_empty_data = {
            'title': 'Заголовок EMPTY',
            'text': 'Просто текст EMPTY.',
            'slug': '',
        }

        cls.form_repeat_data = {
            'title': 'Заголовок INITIAL-NEW',
            'text': 'Просто текст INITIAL-NEW.',
            'slug': NOTE_SLUG,
        }


class TestNoteCreation(GlobalClass, TestCase):

    def test_anonymous_user_cant_create_note(self):
        self.assertEqual(
            self.anonymous_client.post(
                NOTES_ADD,
                data=self.form_data
            ).status_code,
            HTTPStatus.FOUND
        )

    def test_user_can_create_note(self):
        self.client_author.post(NOTES_ADD, data=self.form_data)
        note = Note.objects.filter(slug=self.form_data['slug']).first()
        self.assertNotEqual(note, None)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)

    def test_slug_is_not_none(self):
        self.client_author.post(NOTES_ADD, data=self.form_empty_data)
        note = Note.objects.filter(
            slug=slugify(self.form_empty_data['title'])
        ).first()
        self.assertNotEqual(note, None)
        self.assertEqual(note.title, self.form_empty_data['title'])
        self.assertEqual(note.text, self.form_empty_data['text'])
        self.assertEqual(note.author, self.author)

    def test_slug_is_not_repeat(self):
        self.assertEqual(
            self.client_author.post(
                NOTES_ADD,
                data=self.form_repeat_data
            ).context.get('form').errors['slug'][0],
            self.form_repeat_data['slug'] + WARNING
        )


class TestNoteEditAndDelete(GlobalClass, TestCase):

    def test_user_cant_edit_note_of_another_user(self):
        response = self.client_user.post(NOTES_EDIT, data=self.form_new_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.form_new_data['title'])
        self.assertNotEqual(self.note.text, self.form_new_data['text'])
        self.assertNotEqual(self.note.slug, self.form_new_data['slug'])
        self.assertNotEqual(self.note.author, self.user)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.client_user.delete(NOTES_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertNotEqual(Note.objects.filter(slug=NOTE_SLUG).first(), None)

    def test_author_can_edit_note(self):
        response = self.client_author.post(
            NOTES_EDIT,
            data=self.form_new_data
        )
        self.assertRedirects(response, NOTES_SUCCESS)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_new_data['title'])
        self.assertEqual(self.note.text, self.form_new_data['text'])
        self.assertEqual(self.note.slug, self.form_new_data['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        response = self.client_author.delete(NOTES_DELETE)
        self.assertRedirects(response, NOTES_SUCCESS)
        self.assertEqual(Note.objects.filter(slug=NOTE_SLUG).first(), None)
