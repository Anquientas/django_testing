from datetime import datetime, timedelta

from django.conf import settings
from django.test import Client
from django.urls import reverse
import pytest

from news.models import Comment, News


COUNT_COMMENTS = 222


@pytest.fixture(autouse=True)
def enable_db(db):
    ...


@pytest.fixture
def comment_delete(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def news_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment_edit(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news_home():
    return reverse('news:home')


@pytest.fixture
def users_login():
    return reverse('users:login')


@pytest.fixture
def users_logout():
    return reverse('users:logout')


@pytest.fixture
def users_signup():
    return reverse('users:signup')


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def client_author(author):
    client = Client()
    client.force_login(user=author)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def client_reader(reader):
    client = Client()
    client.force_login(user=reader)
    return client


@pytest.fixture
def client_anonymous():
    return Client()


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )


@pytest.fixture
def several_news():
    return [
        News.objects.create(
            title='Заголовок',
            text='Текст заметки',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def several_comments(news, author):
    return [
        Comment.objects.create(
            news=news,
            author=author,
            text='Текст комментария',
            created=datetime.today() - timedelta(days=index)
        )
        for index in range(COUNT_COMMENTS)
    ]
