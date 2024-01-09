from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


BAD_WORD_DATA = {'text': 'Текст, {bad_word}, остаток текста'}

FORM_DATA = {'text': 'Текст комментария'}
FORM_NEW_DATA = {'text': 'Новый текст комментария'}


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_by_bad_words(client_author, bad_word, news_detail_url):
    BAD_WORD_DATA['text'] = BAD_WORD_DATA['text'].format(bad_word=bad_word)

    # Act
    response = client_author.post(
        news_detail_url,
        data=BAD_WORD_DATA
    )

    assert response.context['form'].errors['text'][0] == WARNING
    assert Comment.objects.count() == 0


def test_anonymous_client_cant_create_comment(client,
                                              news_detail_url):
    # Act
    response = client.post(news_detail_url, data=FORM_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_client_can_create_comment(client_reader,
                                   reader,
                                   news_detail_url):
    # Act
    response = client_reader.post(news_detail_url, data=FORM_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == FORM_DATA['text']
    assert Comment.objects.get().author == reader


def test_author_can_edit_your_comment(client_author,
                                      author,
                                      comment_edit_url,
                                      comment):
    assert client_author.post(
        comment_edit_url,
        data=FORM_NEW_DATA
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == FORM_NEW_DATA['text']
    assert Comment.objects.get().author == author


def test_author_can_delete_your_comment(client_author,
                                        comment_delete_url,
                                        comment):
    assert client_author.post(
        comment_delete_url
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_reader_cant_edit_authors_comment(client_reader,
                                          reader,
                                          comment_edit_url,
                                          comment):
    assert client_reader.post(
        comment_edit_url,
        data=FORM_NEW_DATA
    ).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text != FORM_NEW_DATA['text']
    assert Comment.objects.get().author != reader


def test_reader_cant_delete_authors_comment(client_reader,
                                            reader,
                                            comment_delete_url,
                                            comment):
    assert client_reader.post(
        comment_delete_url
    ).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == FORM_DATA['text']
    assert Comment.objects.get().author != reader
