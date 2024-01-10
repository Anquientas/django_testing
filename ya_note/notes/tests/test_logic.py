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
        notes = list(Note.objects.all())
        self.client_author.post(NOTES_ADD, data=form)
        note = list(set(Note.objects.all()).difference(notes))
        self.assertEqual(len(note), 1)
        note = note[0]
        self.assertEqual(note.title, form['title'])
        self.assertEqual(note.text, form['text'])
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, expected_slug)

    def test_anonymous_client_cant_create_note(self):
        notes_old = list(Note.objects.all())
        notes_old_count = Note.objects.count()
        self.assertEqual(
            self.client_anonymous.post(
                NOTES_ADD,
                data=self.form_data
            ).status_code,
            HTTPStatus.FOUND
        )
        notes = list(Note.objects.all())
        self.assertEqual(notes_old_count, Note.objects.count())
        self.assertEqual(
            notes_old_count,
            len(set(notes).intersection(notes_old))
        )
        self.assertEqual(
            len(
                [
                    note for note in notes
                    if (note.slug == self.form_data['slug']
                        and note.title == self.form_data['title']
                        and note.text == self.form_data['text'])
                ]
            ),
            0
        )

    def test_client_can_create_note(self):
        self.base_check_create_note(self.form_data, self.form_data['slug'])

    def test_create_note_with_slug_is_none(self):
        self.base_check_create_note(
            self.form_empty_data,
            slugify(self.form_empty_data['title'])
        )

    def test_create_note_with_repeat_slug(self):
        notes_old = list(Note.objects.all())
        notes_old_count = Note.objects.count()
        self.assertEqual(
            self.client_author.post(
                NOTES_ADD,
                data=self.form_repeat_data
            ).context.get('form').errors['slug'][0],
            self.form_repeat_data['slug'] + WARNING
        )
        notes = list(Note.objects.all())
        self.assertEqual(notes_old_count, Note.objects.count())
        self.assertEqual(
            notes_old_count,
            len(set(notes).intersection(notes_old))
        )
        self.assertEqual(
            len(
                [
                    note for note in notes
                    if note.slug == self.form_repeat_data['slug']
                ]
            ),
            1
        )

    def test_client_cant_edit_note_of_another_client(self):
        notes_old = list(Note.objects.all())
        notes_old_count = Note.objects.count()
        response = self.client_reader.post(NOTES_EDIT, data=self.form_new_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes = list(Note.objects.all())
        self.assertEqual(notes_old_count, Note.objects.count())
        self.assertEqual(
            len(
                set(
                    [note.slug for note in notes]
                ).difference(
                    [note.slug for note in notes_old]
                )
            ),
            0
        )
        self.assertEqual(
            len(
                set(
                    [note.title for note in notes]
                ).difference(
                    [note.title for note in notes_old]
                )
            ),
            0
        )
        self.assertEqual(
            len(
                set(
                    [note.text for note in notes]
                ).difference(
                    [note.text for note in notes_old]
                )
            ),
            0
        )

    def test_client_cant_delete_note_of_another_client(self):
        notes_old = list(Note.objects.all())
        notes_old_count = Note.objects.count()
        response = self.client_reader.delete(NOTES_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes = list(Note.objects.all())
        self.assertEqual(notes_old_count, Note.objects.count())
        self.assertEqual(
            notes_old_count,
            len(set(notes).intersection(notes_old))
        )

    def test_author_can_edit_note(self):
        notes_old = list(Note.objects.all())
        notes_old_count = Note.objects.count()
        response = self.client_author.post(
            NOTES_EDIT,
            data=self.form_new_data
        )
        self.assertRedirects(response, NOTES_SUCCESS)
        notes = list(Note.objects.all())
        self.assertEqual(notes_old_count, Note.objects.count())
        slugs_difference = set(
            [note.slug for note in notes]
        ).difference(
            [note.slug for note in notes_old]
        )
        self.assertEqual(len(slugs_difference), 1)
        note = [
            note for note in notes if note.slug == list(slugs_difference)[0]
        ]
        self.assertEqual(len(note), 1)
        note = note[0]
        self.assertEqual(note.title, self.form_new_data['title'])
        self.assertEqual(note.text, self.form_new_data['text'])
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, self.form_new_data['slug'])

    def test_author_can_delete_note(self):
        notes_old = list(Note.objects.all())
        notes_old_count = Note.objects.count()
        response = self.client_author.delete(NOTES_DELETE)
        self.assertRedirects(response, NOTES_SUCCESS)
        notes = list(Note.objects.all())
        self.assertEqual(notes_old_count - Note.objects.count(), 1)
        notes_difference = set(notes_old).difference(notes)
        self.assertEqual(len(notes_difference), 1)
        note = list(notes_difference)[0]
        self.assertNotIn(note, notes)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note.slug)
