from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Просто текст.'
    NOTE_SLUG = ''

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='У. Черчиль')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.create_url = reverse('notes:add')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.create_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_comment(self):
        self.auth_client.post(self.create_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_slug_is_not_none(self):
        self.auth_client.post(self.create_url, data=self.form_data)
        note = Note.objects.get()
        if self.NOTE_SLUG == '':
            slug = slugify(self.NOTE_TITLE)[:100]
        else:
            slug = self.NOTE_SLUG[:100]
        self.assertEqual(note.slug, slug)

    def test_slug_is_not_repeat(self):
        self.auth_client.post(self.create_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.auth_client.post(self.create_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditAndDelete(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TITLE_NEW = 'Новый заголовок'
    NOTE_TEXT = 'Просто текст.'
    NOTE_TEXT_NEW = 'Просто новый текст.'
    NOTE_SLUG = 'Slug'
    NOTE_SLUG_NEW = 'New_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='У. Черчиль')
        cls.client_author = Client()
        cls.client_author.force_login(user=cls.author)

        cls.user = User.objects.create(username='Читатель заметки')
        cls.client_user = Client()
        cls.client_user.force_login(user=cls.user)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author,
        )
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success', args=None)
        cls.form_data = {
            'title': cls.NOTE_TITLE_NEW,
            'text': cls.NOTE_TEXT_NEW,
            'slug': cls.NOTE_SLUG_NEW,
        }

    def test_user_cant_edit_note_of_another_user(self):
        response = self.client_user.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.client_user.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.client_author.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE_NEW)
        self.assertEqual(self.note.text, self.NOTE_TEXT_NEW)
        self.assertEqual(self.note.slug, self.NOTE_SLUG_NEW)

    def test_author_can_delete_note(self):
        response = self.client_author.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 0)
