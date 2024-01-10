from http import HTTPStatus

from notes.forms import WARNING
from notes.models import Note
from .base import (
    BaseTestCase,
    NOTES_ADD,
    NOTES_DELETE,
    NOTES_EDIT,
    NOTES_SUCCESS,
)


class TestNoteCreation(BaseTestCase):

    def check_group_asserts(self, note_initial, note, form):
        self.assertEqual(note.title, form['title'])
        self.assertEqual(note.text, form['text'])
        self.assertEqual(note.author, note_initial.author)
        return True

    def test_anonymous_client_cant_create_note(self):
        notes = Note.objects.get()
        notes_count = Note.objects.count()
        self.assertEqual(
            self.client_anonymous.post(
                NOTES_ADD,
                data=self.form_data
            ).status_code,
            HTTPStatus.FOUND
        )
        self.assertEqual(notes, Note.objects.get())
        self.assertEqual(notes_count, Note.objects.count())

    def test_client_can_create_note(self):
        note_count = Note.objects.count()
        self.client_author.post(NOTES_ADD, data=self.form_data)
        self.assertEqual(Note.objects.count() - note_count, 1)
        note = Note.objects.exclude(id=self.note.id)[0]
        if self.check_group_asserts(self.note, note, self.form_data):
            self.assertEqual(note.slug, self.form_data['slug'])

    def test_create_note_with_slug_is_none(self):
        note_count = Note.objects.count()
        self.client_author.post(NOTES_ADD, data=self.form_empty_data)
        self.assertEqual(Note.objects.count() - note_count, 1)
        note = Note.objects.exclude(id=self.note.id)[0]
        if self.check_group_asserts(self.note, note, self.form_empty_data):
            self.assertNotEqual(note.slug, self.form_empty_data['slug'])

    def test_create_note_with_repeat_slug(self):
        note_count = Note.objects.count()
        self.assertEqual(
            self.client_author.post(
                NOTES_ADD,
                data=self.form_repeat_data
            ).context.get('form').errors['slug'][0],
            self.form_repeat_data['slug'] + WARNING
        )
        self.assertEqual(Note.objects.count(), note_count)

    def test_client_cant_edit_note_of_another_client(self):
        self.assertEqual(self.client_reader.post(
            NOTES_EDIT,
            data=self.form_new_data
        ).status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.get(), self.note)

    def test_client_cant_delete_note_of_another_client(self):
        note_count = Note.objects.count()
        response = self.client_reader.delete(NOTES_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), note_count)
        note = Note.objects.filter(
            slug=response.resolver_match.kwargs['slug']
        )[0]
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_author_can_edit_note(self):
        response = self.client_author.post(
            NOTES_EDIT,
            data=self.form_new_data
        )
        self.assertRedirects(response, NOTES_SUCCESS)
        note = Note.objects.get()
        if self.check_group_asserts(self.note, note, self.form_new_data):
            self.assertEqual(note.slug, self.form_new_data['slug'])

    def test_author_can_delete_note(self):
        note_count = Note.objects.count()
        response = self.client_author.delete(NOTES_DELETE)
        self.assertRedirects(response, NOTES_SUCCESS)
        self.assertEqual(note_count - Note.objects.count(), 1)
