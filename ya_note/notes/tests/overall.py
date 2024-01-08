from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note
from .urls import NOTE_SLUG


User = get_user_model()


class Overall(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='У. Черчиль')
        cls.client_author = Client()
        cls.client_author.force_login(user=cls.author)

        # cls.author_2 = User.objects.create(username='А. Веллингтон')
        # cls.client_author_2 = Client()
        # cls.client_author_2.force_login(user=cls.author_2)

        cls.reader = User.objects.create(username='Читатель заметки')
        cls.client_reader = Client()
        cls.client_reader.force_login(user=cls.reader)

        # cls.client_anonymous = Client()

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Просто текст.',
            slug=NOTE_SLUG,
            author=cls.author,
        )

        # all_notes = [
        #     Note(
        #         title=f'Заголовок {index}',
        #         text='Просто текст.',
        #         slug=NOTE_SLUG + f'_{index}',
        #         author=cls.author,
        #     )
        #     if index % 2 == 1 else
        #     Note(
        #         title=f'Заголовок {index}',
        #         text='Просто текст.',
        #         slug=NOTE_SLUG + f'_{index}',
        #         author=cls.author_2,
        #     )
        #     for index in range(4)
        # ]
        # cls.notes = Note.objects.bulk_create(all_notes)
