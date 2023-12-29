import pytest

from http import HTTPStatus

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_not_availability_create_comment_for_anonymous_client(client, news):
    url = reverse('news:detail', args=(news.id,))

    # Act
    response = client.get(url)

    assert 'form' not in response.context


@pytest.mark.django_db
def test_availability_create_comment_for_user(news, reader_client):
    url = reverse('news:detail', args=(news.id,))

    # Act
    response = reader_client.get(url)

    assert 'form' in response.context


@pytest.mark.django_db
def test_by_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Текст, {BAD_WORDS[0]}, остаток текста'}

    # Act
    response = author_client.post(url, data=bad_words_data)
    comments_count = Comment.objects.count()

    assert response.context['form'].errors['text'][0] == WARNING
    assert comments_count == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_pages_availability_for_author(author_client, comment, name):
    url = reverse(name, args=(comment.id,))

    # Act
    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_pages_no_availability_for_reader(comment, name, reader_client):
    url = reverse(name, args=(comment.id,))

    # Act
    response = reader_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
