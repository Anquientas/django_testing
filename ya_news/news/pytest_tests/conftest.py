from django.test import Client
from django.urls import reverse
import pytest

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db(db):
    ...


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
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


# @pytest.fixture
# def comment_id_for_args(comment):
#     return comment.id,


@pytest.fixture
def NEWS_PK(news):
    return news.id


@pytest.fixture
def COMMENT_PK(comment):
    return comment.id


@pytest.fixture
def NEWS_HOME():
    return reverse('news:home')


@pytest.fixture
def NEWS_DETAIL(NEWS_PK):
    return reverse('news:detail', args=(NEWS_PK,))


@pytest.fixture
def COMMENT_DELETE(COMMENT_PK):
    return reverse('news:delete', args=(COMMENT_PK,))


@pytest.fixture
def COMMENT_EDIT(COMMENT_PK):
    return reverse('news:edit', args=(COMMENT_PK,))


# NEWS_HOME = reverse('news:home')
# NEWS_DETAIL = reverse('news:detail', args=(NEWS_PK,))
# COMMENT_DELETE = reverse('news:delete', args=(COMMENT_PK,))
# COMMENT_EDIT = reverse('news:edit', args=(COMMENT_PK,))

# USERS_LOGIN = reverse('users:login')
# USERS_LOGOUT = reverse('users:logout')
# USERS_SIGNUP = reverse('users:signup')


@pytest.fixture
def USERS_LOGIN():
    return reverse('users:login')


@pytest.fixture
def USERS_LOGOUT():
    return reverse('users:logout')


@pytest.fixture
def USERS_SIGNUP():
    return reverse('users:signup')
