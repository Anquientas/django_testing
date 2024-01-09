from notes.models import Note
from notes.forms import NoteForm
from .base import (
    BaseTestCase,
    NOTE_SLUG,
    NOTES_ADD,
    NOTES_EDIT,
    NOTES_LIST,
)


class Base(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        BaseTestCase.setUpTestData()

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
        note = notes.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note.slug)

    def test_notes_not_available_for_another_author(self):
        response = self.client_reader.get(NOTES_LIST)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_form_include_page(self):
        urls = (NOTES_ADD, NOTES_EDIT)
        for url in urls:
            with self.subTest(url=url):
                context = self.client_author.get(url).context
                self.assertIn('form', context)
                self.assertIs(type(context['form']), NoteForm)
