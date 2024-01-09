from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News


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
    comment_new = Comment.objects.get()
    assert comment_new.text == FORM_DATA['text']
    assert comment_new.news == News.objects.get()
    assert comment_new.author == reader


def test_author_can_edit_your_comment(client_author,
                                      author,
                                      comment_edit_url,
                                      comment):
    assert client_author.post(
        comment_edit_url,
        data=FORM_NEW_DATA
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment_edit = Comment.objects.get()
    assert comment_edit.text == FORM_NEW_DATA['text']
    assert comment_edit.news == News.objects.get()
    assert comment_edit.author == author


def test_author_can_delete_your_comment(client_author,
                                        comment_delete_url,
                                        comment):
    assert client_author.post(
        comment_delete_url
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_reader_cant_edit_authors_comment(client_reader,
                                          comment_edit_url,
                                          comment):
    text_old = comment.text
    news_old = comment.news
    author_old = comment.author
    assert client_reader.post(
        comment_edit_url,
        data=FORM_NEW_DATA
    ).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    comment_cant_edit = Comment.objects.get()
    assert comment_cant_edit.text == text_old
    assert comment_cant_edit.news == news_old
    assert comment_cant_edit.author == author_old
    # assert Comment.objects.get().text != FORM_NEW_DATA['text']
    # assert Comment.objects.get().author != reader


def test_reader_cant_delete_authors_comment(client_reader,
                                            comment_delete_url,
                                            comment):
    text_old = comment.text
    news_old = comment.news
    author_old = comment.author
    assert client_reader.post(
        comment_delete_url
    ).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    comment_cant_delete = Comment.objects.get()
    assert comment_cant_delete.text == text_old
    assert comment_cant_delete.news == news_old
    assert comment_cant_delete.author == author_old
