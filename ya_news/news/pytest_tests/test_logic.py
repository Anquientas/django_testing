from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


COMMENT_DELETE = pytest.lazy_fixture('comment_delete')
COMMENT_EDIT = pytest.lazy_fixture('comment_edit')
NEWS_DETAIL = pytest.lazy_fixture('news_detail')
NEWS_HOME = pytest.lazy_fixture('news_home')

BAD_WORD_DATA = 'Текст, {bad_word}, остаток текста'
WORDS_DATA = 'Текст комментария'
WORDS_DATA_NEW = 'Новый текст комментария'


@pytest.mark.parametrize('bad_word', BAD_WORDS)
@pytest.mark.parametrize('url', [NEWS_DETAIL])
def test_by_bad_words(client_author, bad_word, url):
    bad_word_data = {'text': BAD_WORD_DATA.format(bad_word=bad_word)}

    # Act
    response = client_author.post(url, data=bad_word_data)

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
