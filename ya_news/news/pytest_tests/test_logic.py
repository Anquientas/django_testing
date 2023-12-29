import pytest

from django.urls import reverse

from news.models import Comment


from http import HTTPStatus

from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_not_availability_create_comment_for_anonymous_client(client, news):
    url = reverse('news:detail', args=(news.id,))

    # Act
    response = client.get(url)

    assert 'form' not in response.context


@pytest.mark.django_db
def test_availability_create_comment_for_user(reader_client, news):
    url = reverse('news:detail', args=(news.id,))

    # Act
    response = reader_client.get(url)

    assert 'form' in response.context


@pytest.mark.django_db
def test_by_bad_words(news, author_client):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Текст, {BAD_WORDS[0]}, остаток текста'}
    response = author_client.post(url, data=bad_words_data)
    comments_count = Comment.objects.count()

    # Act

    print(response.context['form'])

    assert response.context['form'].errors['text'][0] == WARNING
    assert comments_count == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_pages_availability_for_author(author_client, name, comment):
    url = reverse(name, args=(comment.id,))

    # Act
    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_pages_no_availability_for_reader(reader_client, name, comment):
    url = reverse(name, args=(comment.id,))

    # Act
    response = reader_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
