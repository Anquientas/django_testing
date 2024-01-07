from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestListNotes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author_1 = User.objects.create(username='У. Черчиль')
        cls.author_2 = User.objects.create(username='А. Веллингтон')

        all_notes = [
            Note(
                title=f'Заголовок {index}',
                text='Просто текст.',
                slug=f'Slug_{index}',
                author=cls.author_1,
            )
            if index % 2 == 1 else
            Note(
                title=f'Заголовок {index}',
                text='Просто текст.',
                slug=f'Slug_{index}',
                author=cls.author_2,
            )
            for index in range(4)
        ]
        cls.notes = Note.objects.bulk_create(all_notes)

    def test_notes_one_author(self):
        self.client.force_login(self.author_1)
        response = self.client.get(reverse('notes:list'))
        notes = response.context['object_list']
        for note in notes:
            self.assertNotEqual(note.author, self.author_2)

    def test_object_in_list_objects_is_note(self):
        self.client.force_login(self.author_1)
        response = self.client.get(reverse('notes:list'))
        notes = response.context['object_list']
        self.assertIsInstance(notes[0], Note)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='У. Черчиль')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Просто текст.',
            slug='Slug',
            author=cls.author,
        )
        cls.urls = [
            ('notes:add', None),
            ('notes:edit', (cls.note.slug,)),
        ]

    def test_form_include_page(self):
        self.client.force_login(self.author)
        for name, args in self.urls:
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=args))
                self.assertIn('form', response.context)
