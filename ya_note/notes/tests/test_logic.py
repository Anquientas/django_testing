from http import HTTPStatus

from django.test import Client

from notes.forms import WARNING
from notes.models import Note
from .base import (
    BaseTestCase,
    NOTE_SLUG,
    NOTES_ADD,
    NOTES_DELETE,
    NOTES_EDIT,
    NOTES_SUCCESS,
)

from django.db.models import Q


class TestNoteCreation(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        BaseTestCase.setUpTestData()
        cls.client_anonymous = Client()

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
            'title': 'Заголовок INITIAL',
            'text': 'Просто текст INITIAL.',
            'slug': NOTE_SLUG,
        }

    def test_anonymous_user_cant_create_note(self):
        self.assertEqual(
            self.client_anonymous.post(
                NOTES_ADD,
                data=self.form_data
            ).status_code,
            HTTPStatus.FOUND
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_user_can_create_note(self):
        self.client_author.post(NOTES_ADD, data=self.form_data)
        self.assertEqual(Note.objects.count(), 2)
        note = Note.objects.filter(~Q(id=self.note.id))[0]
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_slug_is_not_none(self):
        self.client_author.post(NOTES_ADD, data=self.form_empty_data)
        self.assertEqual(Note.objects.count(), 2)
        note = Note.objects.filter(~Q(id=self.note.id))[0]
        self.assertEqual(note.title, self.form_empty_data['title'])
        self.assertEqual(note.text, self.form_empty_data['text'])
        self.assertNotEqual(note.slug, self.form_empty_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_slug_is_not_repeat(self):
        self.assertEqual(
            self.client_author.post(
                NOTES_ADD,
                data=self.form_repeat_data
            ).context.get('form').errors['slug'][0],
            self.form_repeat_data['slug'] + WARNING
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.client_reader.post(NOTES_EDIT, data=self.form_new_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        note = Note.objects.get()
        self.assertNotEqual(note.title, self.form_new_data['title'])
        self.assertNotEqual(note.text, self.form_new_data['text'])
        self.assertNotEqual(note.slug, self.form_new_data['slug'])
        self.assertNotEqual(note.author, self.reader)

    def test_user_cant_delete_note_of_another_user(self):
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        title_old = note.title
        text_old = note.text
        slug_old = note.slug
        author_old = note.author
        response = self.client_reader.delete(NOTES_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, title_old)
        self.assertEqual(note.text, text_old)
        self.assertEqual(note.slug, slug_old)
        self.assertEqual(note.author, author_old)

    def test_author_can_edit_note(self):
        self.assertEqual(Note.objects.count(), 1)
        author_old = Note.objects.get().author
        response = self.client_author.post(
            NOTES_EDIT,
            data=self.form_new_data
        )
        self.assertRedirects(response, NOTES_SUCCESS)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_new_data['title'])
        self.assertEqual(self.note.text, self.form_new_data['text'])
        self.assertEqual(self.note.slug, self.form_new_data['slug'])
        self.assertEqual(self.note.author, author_old)

    def test_author_can_delete_note(self):
        response = self.client_author.delete(NOTES_DELETE)
        self.assertRedirects(response, NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), 0)
