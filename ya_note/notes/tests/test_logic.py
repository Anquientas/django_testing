from http import HTTPStatus

from pytils.translit import slugify

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

    def base_check_create_note(self, form, expected_slug):
        notes_old = set(Note.objects.all())
        self.client_author.post(NOTES_ADD, data=form)
        note = set(Note.objects.all()) - notes_old
        self.assertEqual(len(note), 1)
        note = note.pop()
        self.assertEqual(note.title, form['title'])
        self.assertEqual(note.text, form['text'])
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, expected_slug)

    def test_anonymous_client_cant_create_note(self):
        notes_old = set(Note.objects.all())
        # notes_old_count = Note.objects.count()
        self.assertEqual(
            self.client_anonymous.post(
                NOTES_ADD,
                data=self.form_data
            ).status_code,
            HTTPStatus.FOUND
        )
        self.assertEqual(len(set(Note.objects.all()) - notes_old), 0)

    def test_client_can_create_note(self):
        self.base_check_create_note(self.form_data, self.form_data['slug'])

    def test_create_note_with_slug_is_none(self):
        self.base_check_create_note(
            self.form_empty_data,
            slugify(self.form_empty_data['title'])
        )

    def test_create_note_with_repeat_slug(self):
        notes_old = set(Note.objects.all())
        self.assertEqual(
            self.client_author.post(
                NOTES_ADD,
                data=self.form_repeat_data
            ).context.get('form').errors['slug'][0],
            self.form_repeat_data['slug'] + WARNING
        )
        self.assertEqual(len(set(Note.objects.all()) - notes_old), 0)

    def test_client_cant_edit_note_of_another_client(self):
        notes_old = set(Note.objects.all())
        response = self.client_reader.post(NOTES_EDIT, data=self.form_new_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(len(set(Note.objects.all()) - notes_old), 0)
        note = Note.objects.get(
            slug=response.request['PATH_INFO'].split('/')[-2]
        )
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note.slug)

    def test_client_cant_delete_note_of_another_client(self):
        notes_old = set(Note.objects.all())
        response = self.client_reader.delete(NOTES_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(len(notes_old - set(Note.objects.all())), 0)

    def test_author_can_edit_note(self):
        notes_old = set(Note.objects.all())
        notes_old_slug = set([note.slug for note in list(notes_old)])
        response = self.client_author.post(
            NOTES_EDIT,
            data=self.form_new_data
        )
        self.assertRedirects(response, NOTES_SUCCESS)
        notes_new = set(Note.objects.all())
        self.assertEqual(notes_new, notes_old)
        notes_new_slug = set([note.slug for note in list(notes_new)])
        self.assertEqual(len(notes_new_slug - notes_old_slug), 1)
        note = Note.objects.get(slug=(notes_new_slug - notes_old_slug).pop())
        self.assertEqual(note.title, self.form_new_data['title'])
        self.assertEqual(note.text, self.form_new_data['text'])
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, self.form_new_data['slug'])

    def test_author_can_delete_note(self):
        notes_old = set(Note.objects.all())
        response = self.client_author.delete(NOTES_DELETE)
        self.assertRedirects(response, NOTES_SUCCESS)
        notes = set(Note.objects.all())
        note = notes_old - notes
        self.assertEqual(len(note), 1)
        self.assertFalse(
            Note.objects.filter(
                slug=response.request['PATH_INFO'].split('/')[-2]
            ).exists()
        )
