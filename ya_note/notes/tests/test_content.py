from notes.models import Note
from .base import Overall
from .urls import (
    NOTE_SLUG,
    NOTES_ADD,
    NOTES_EDIT,
    NOTES_LIST,
)


class Base(Overall):

    @classmethod
    def setUpTestData(cls):
        Overall.setUpTestData()

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
                author=cls.reader,
            )
            for index in range(4)
        ]
        cls.notes = Note.objects.bulk_create(all_notes)


class TestListNotes(Base):

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


class TestDetailPage(Base):

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
