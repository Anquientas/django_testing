from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note
from .urls import (
    NOTE_SLUG,
    NOTES_ADD,
    NOTES_EDIT,
    NOTES_LIST,
)


User = get_user_model()


class Global(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='У. Черчиль')
        cls.client_author = Client()
        cls.client_author.force_login(user=cls.author)

        cls.author_2 = User.objects.create(username='А. Веллингтон')
        cls.client_author_2 = Client()
        cls.client_author_2.force_login(user=cls.author_2)

        cls.reader = User.objects.create(username='Читатель заметки')
        cls.reader_client = Client()
        cls.reader_client.force_login(user=cls.reader)

        cls.anonymous_client = Client()

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Просто текст.',
            slug=NOTE_SLUG,
            author=cls.author,
        )

        all_notes = [
            Note(
                title=f'Заголовок {index}',
                text='Просто текст.',
                slug=NOTE_SLUG + f'_{index}',
                author=cls.author,
            )
            if index % 2 == 1 else
            Note(
                title=f'Заголовок {index}',
                text='Просто текст.',
                slug=NOTE_SLUG + f'_{index}',
                author=cls.author_2,
            )
            for index in range(4)
        ]
        cls.notes = Note.objects.bulk_create(all_notes)


class TestListNotes(Global, TestCase):

    def test_notes_one_author(self):
        response = self.client_author.get(NOTES_LIST)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)
        note = notes.get(slug=NOTE_SLUG)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)

    def test_object_in_list_objects_is_note(self):
        response = self.client_author.get(NOTES_LIST)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)
        note = notes.get(slug=NOTE_SLUG)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)


class TestDetailPage(Global, TestCase):

    def test_form_include_page(self):
        urls = (NOTES_ADD, NOTES_EDIT)
        for url in urls:
            with self.subTest(url=url):
                self.assertIn('form', self.client_author.get(url).context)
                self.assertIn(
                    'title',
                    self.client_author.get(url).context['form'].fields.keys()
                )
                self.assertIn(
                    'text',
                    self.client_author.get(url).context['form'].fields.keys()
                )
                self.assertIn(
                    'slug',
                    self.client_author.get(url).context['form'].fields.keys()
                )
