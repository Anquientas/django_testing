from http import HTTPStatus

from django.urls import reverse
import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


BAD_WORD_DATA = 'Текст, {bad_word}, остаток текста'


# def test_not_availability_create_comment_for_anonymous_client(client, news):
#     url = reverse('news:detail', args=(news.id,))

#     # Act
#     response = client.get(url)

#     assert 'form' not in response.context


# @pytest.mark.django_db
# def test_availability_create_comment_for_user(news, reader_client):
#     url = reverse('news:detail', args=(news.id,))

#     # Act
#     response = reader_client.get(url)

#     assert 'form' in response.context


@pytest.mark.parametrize(
    'bad_word', BAD_WORDS,
)
def test_by_bad_words(client_author, NEWS_DETAIL, bad_word):
    url = NEWS_DETAIL
    # bad_word_data = {'text': f'Текст, {BAD_WORD}, остаток текста'}
    bad_word_data = {'text': BAD_WORD_DATA.format(bad_word=bad_word)}

    # Act
    response = client_author.post(url, data=bad_word_data)
    comments_count = Comment.objects.count()

    assert response.context['form'].errors['text'][0] == WARNING
    assert comments_count == 0


# @pytest.mark.django_db
# @pytest.mark.parametrize(
#     'name',
#     ('news:edit', 'news:delete')
# )
# def test_pages_availability_for_author(author_client, comment, name):
#     url = reverse(name, args=(comment.id,))

#     # Act
#     response = author_client.get(url)

#     assert response.status_code == HTTPStatus.OK


# @pytest.mark.django_db
# @pytest.mark.parametrize(
#     'name',
#     ('news:edit', 'news:delete')
# )
# def test_pages_no_availability_for_reader(comment, name, reader_client):
#     url = reverse(name, args=(comment.id,))

#     # Act
#     response = reader_client.get(url)

#     assert response.status_code == HTTPStatus.NOT_FOUND
