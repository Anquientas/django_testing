from http import HTTPStatus

from pytils.translit import slugify

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


class TestNoteCreation(BaseTestCase):

    def base_check_create_note(self, form, expected_slug):
        notes = set(Note.objects.all())
        self.client_author.post(NOTES_ADD, data=form)
        notes = set(Note.objects.all()) - notes
        self.assertEqual(len(notes), 1)
        note = notes.pop()
        self.assertEqual(note.title, form['title'])
        self.assertEqual(note.text, form['text'])
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, expected_slug)

    def test_anonymous_client_cant_create_note(self):
        notes = set(Note.objects.all())
        self.assertEqual(
            self.client_anonymous.post(
                NOTES_ADD,
                data=self.form_data
            ).status_code,
            HTTPStatus.FOUND
        )
        self.assertEqual(set(Note.objects.all()), notes)

    def test_client_can_create_note(self):
        self.base_check_create_note(self.form_data, self.form_data['slug'])

    def test_create_note_with_slug_is_none(self):
        self.base_check_create_note(
            self.form_empty_data,
            slugify(self.form_empty_data['title'])
        )

    def test_create_note_with_repeat_slug(self):
        notes = set(Note.objects.all())
        self.assertEqual(
            self.client_author.post(
                NOTES_ADD,
                data=self.form_repeat_data
            ).context.get('form').errors['slug'][0],
            self.form_repeat_data['slug'] + WARNING
        )
        self.assertEqual(set(Note.objects.all()), notes)

    def test_client_cant_edit_note_of_another_client(self):
        note_old = Note.objects.get(slug=NOTE_SLUG)
        notes = set(Note.objects.all())
        response = self.client_reader.post(
            NOTES_EDIT,
            data=self.form_new_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(set(Note.objects.all()), notes)
        note = Note.objects.get(id=note_old.id)
        self.assertEqual(note.title, note_old.title)
        self.assertEqual(note.text, note_old.text)
        self.assertEqual(note.author, note_old.author)
        self.assertEqual(note.slug, note_old.slug)

    def test_client_cant_delete_note_of_another_client(self):
        notes = set(Note.objects.all())
        note_old = Note.objects.get(slug=NOTE_SLUG)
        response = self.client_reader.delete(NOTES_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(set(Note.objects.all()), notes)
        note = Note.objects.get(id=note_old.id)
        self.assertEqual(note.title, note_old.title)
        self.assertEqual(note.text, note_old.text)
        self.assertEqual(note.author, note_old.author)
        self.assertEqual(note.slug, note_old.slug)

    def test_author_can_edit_note(self):
        note_id = set(
            Note.objects.filter(slug=NOTE_SLUG).values_list('id', flat=True)
        ).pop()
        response = self.client_author.post(
            NOTES_EDIT,
            data=self.form_new_data
        )
        self.assertRedirects(response, NOTES_SUCCESS)
        note = Note.objects.get(id=note_id)
        self.assertEqual(note.title, self.form_new_data['title'])
        self.assertEqual(note.text, self.form_new_data['text'])
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.form_new_data['slug'])

    def test_author_can_delete_note(self):
        note_id = set(
            Note.objects.filter(slug=NOTE_SLUG).values_list('id', flat=True)
        ).pop()
        notes_count = Note.objects.count()
        response = self.client_author.delete(NOTES_DELETE)
        self.assertRedirects(response, NOTES_SUCCESS)
        self.assertEqual(notes_count - Note.objects.count(), 1)
        self.assertFalse(Note.objects.filter(id=note_id).exists())
