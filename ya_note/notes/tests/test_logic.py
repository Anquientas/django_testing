from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from django.urls import reverse_lazy

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
        # notes_count = Note.objects.count()
        # self.assertEqual(notes_count, 1)
        self.auth_client.post(self.create_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditAndDelete(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Просто текст.'
    NOTE_TEXT_NEW = 'Просто новый текст.'
    NOTE_SLUG = 'Slug'

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
        cls.form_data = {'text': cls.NOTE_TEXT_NEW}

    def test_author_can_edit_note(self):
        response = self.client_author.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT_NEW)

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

    # def test_author_can_edit_note(self):
    #     response = self.client_author.post(self.edit_url, data=self.form_data)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
    #     self.assertRedirects(response, self.success_url)
    #     self.note.refresh_from_db()
    #     self.assertEqual(self.note.text, self.NOTE_TEXT_NEW)

    def test_author_can_delete_note(self):
        response = self.client_author.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 0)










       # # Создаём новость в БД.
        # cls.news = News.objects.create(title='Заголовок', text='Текст')
        # # Формируем адрес блока с комментариями, который понадобится для тестов.
        # news_url = reverse('news:detail', args=(cls.news.id,))  # Адрес новости.
        # cls.url_to_comments = news_url + '#comments'  # Адрес блока с комментариями.
        # # Создаём пользователя - автора комментария.
        # cls.author = User.objects.create(username='Автор комментария')
        # # Создаём клиент для пользователя-автора.
        # cls.author_client = Client()
        # # "Логиним" пользователя в клиенте.
        # cls.author_client.force_login(cls.author)
        # # Делаем всё то же самое для пользователя-читателя.
        # cls.reader = User.objects.create(username='Читатель')
        # cls.reader_client = Client()
        # cls.reader_client.force_login(cls.reader)
        # # Создаём объект комментария.
        # cls.comment = Comment.objects.create(
        #     news=cls.news,
        #     author=cls.author,
        #     text=cls.COMMENT_TEXT
        # )
        # # URL для редактирования комментария.
        # cls.edit_url = reverse('news:edit', args=(cls.comment.id,)) 
        # # URL для удаления комментария.
        # cls.delete_url = reverse('news:delete', args=(cls.comment.id,))  
        # # Формируем данные для POST-запроса по обновлению комментария.
        # cls.form_data = {'text': cls.NEW_COMMENT_TEXT}

















# # news/tests/test_logic.py
# ...
# class TestCommentEditDelete(TestCase):
#     # Тексты для комментариев не нужно дополнительно создавать 
#     # (в отличие от объектов в БД), им не нужны ссылки на self или cls, 
#     # поэтому их можно перечислить просто в атрибутах класса.
#     COMMENT_TEXT = 'Текст комментария'
#     NEW_COMMENT_TEXT = 'Обновлённый комментарий'

#     @classmethod
#     def setUpTestData(cls):
#         # Создаём новость в БД.
#         cls.news = News.objects.create(title='Заголовок', text='Текст')
#         # Формируем адрес блока с комментариями, который понадобится для тестов.
#         news_url = reverse('news:detail', args=(cls.news.id,))  # Адрес новости.
#         cls.url_to_comments = news_url + '#comments'  # Адрес блока с комментариями.
#         # Создаём пользователя - автора комментария.
#         cls.author = User.objects.create(username='Автор комментария')
#         # Создаём клиент для пользователя-автора.
#         cls.author_client = Client()
#         # "Логиним" пользователя в клиенте.
#         cls.author_client.force_login(cls.author)
#         # Делаем всё то же самое для пользователя-читателя.
#         cls.reader = User.objects.create(username='Читатель')
#         cls.reader_client = Client()
#         cls.reader_client.force_login(cls.reader)
#         # Создаём объект комментария.
#         cls.comment = Comment.objects.create(
#             news=cls.news,
#             author=cls.author,
#             text=cls.COMMENT_TEXT
#         )
#         # URL для редактирования комментария.
#         cls.edit_url = reverse('news:edit', args=(cls.comment.id,)) 
#         # URL для удаления комментария.
#         cls.delete_url = reverse('news:delete', args=(cls.comment.id,))  
#         # Формируем данные для POST-запроса по обновлению комментария.
#         cls.form_data = {'text': cls.NEW_COMMENT_TEXT}

#     def test_author_can_delete_comment(self):
#         # От имени автора комментария отправляем DELETE-запрос на удаление.
#         response = self.author_client.delete(self.delete_url)
#         # Проверяем, что редирект привёл к разделу с комментариями.
#         # Заодно проверим статус-коды ответов.
#         self.assertRedirects(response, self.url_to_comments)
#         # Считаем количество комментариев в системе.
#         comments_count = Comment.objects.count()
#         # Ожидаем ноль комментариев в системе.
#         self.assertEqual(comments_count, 0)

#     def test_user_cant_delete_comment_of_another_user(self):
#         # Выполняем запрос на удаление от пользователя-читателя.
#         response = self.reader_client.delete(self.delete_url)
#         # Проверяем, что вернулась 404 ошибка.
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
#         # Убедимся, что комментарий по-прежнему на месте.
#         comments_count = Comment.objects.count()
#         self.assertEqual(comments_count, 1)

#     def test_author_can_edit_comment(self):
#         # Выполняем запрос на редактирование от имени автора комментария.
#         response = self.author_client.post(self.edit_url, data=self.form_data)
#         # Проверяем, что сработал редирект.
#         self.assertRedirects(response, self.url_to_comments)
#         # Обновляем объект комментария.
#         self.comment.refresh_from_db()
#         # Проверяем, что текст комментария соответствует обновленному.
#         self.assertEqual(self.comment.text, self.NEW_COMMENT_TEXT)

#     def test_user_cant_edit_comment_of_another_user(self):
#         # Выполняем запрос на редактирование от имени другого пользователя.
#         response = self.reader_client.post(self.edit_url, data=self.form_data)
#         # Проверяем, что вернулась 404 ошибка.
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
#         # Обновляем объект комментария.
#         self.comment.refresh_from_db()
#         # Проверяем, что текст остался тем же, что и был.
#         self.assertEqual(self.comment.text, self.COMMENT_TEXT)