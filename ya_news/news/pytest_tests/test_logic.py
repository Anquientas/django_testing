from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


COMMENT_DELETE = pytest.lazy_fixture('comment_delete_url')
COMMENT_EDIT = pytest.lazy_fixture('comment_edit_url')
NEWS_DETAIL = pytest.lazy_fixture('news_detail_url')
NEWS_HOME = pytest.lazy_fixture('news_home_url')

BAD_WORD_TEXT = 'Текст, {bad_word}, остаток текста'
BAD_WORD_DATA = {'text': BAD_WORD_TEXT}

WORDS_DATA = 'Текст комментария'
WORDS_DATA_NEW = 'Новый текст комментария'

# CLIENT_ANONYMOUS = pytest.lazy_fixture('client')
# CLIENT_AUTHOR = pytest.lazy_fixture('client_author')
# CLIENT_READER = pytest.lazy_fixture('client_reader')


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_by_bad_words(client_author, bad_word, news_detail_url):
    BAD_WORD_DATA['text'] = BAD_WORD_TEXT.format(bad_word=bad_word)

    # Act
    response = client_author.post(
        news_detail_url,
        data=BAD_WORD_DATA
    )

    assert response.context['form'].errors['text'][0] == WARNING
    assert Comment.objects.count() == 0


@pytest.mark.parametrize('url', [NEWS_DETAIL])
def test_anonymous_client_cant_create_comment(client_anonymous, url):
    form_data = {'text': WORDS_DATA}
    # Act
    response = client_anonymous.post(url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.parametrize('url', [NEWS_DETAIL])
def test_client_can_create_comment(client_reader, url):
    form_data = {'text': WORDS_DATA}
    # Act
    response = client_reader.post(url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == form_data['text']


@pytest.mark.parametrize('url', [COMMENT_EDIT])
def test_author_can_edit_your_comment(client_author, url, comment):
    form_new_data = {'text': WORDS_DATA_NEW}
    # Act
    response = client_author.post(url, data=form_new_data)

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == form_new_data['text']


@pytest.mark.parametrize('url', [COMMENT_DELETE])
def test_author_can_delete_your_comment(client_author, url, comment):
    # Act
    response = client_author.post(url)

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.parametrize('url', [COMMENT_EDIT])
def test_reader_cant_edit_authors_comment(client_reader, url, comment):
    form_new_data = {'text': WORDS_DATA_NEW}
    # Act
    response = client_reader.post(url, data=form_new_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text != form_new_data['text']


@pytest.mark.parametrize('url', [COMMENT_DELETE])
def test_reader_cant_delete_authors_comment(client_reader, url, comment):
    # Act
    response = client_reader.post(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == WORDS_DATA
