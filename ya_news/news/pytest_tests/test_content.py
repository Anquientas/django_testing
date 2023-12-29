import pytest

from django.urls import reverse

from datetime import datetime, timedelta

from django.conf import settings

from news.models import Comment, News


# assert response.status_code != 200, response.context['form'].errors
@pytest.mark.django_db
def test_vount_news_on_home_page(client):
    all_news = [
        News.objects.create(
            title='Заголовок',
            text='Текст заметки',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]

    # Act
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = len(object_list)

    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_sort_news_on_home_page(client):
    all_news = [
        News.objects.create(
            title='Заголовок',
            text='Текст заметки',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]

    # Act
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)

    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_sort_comments(client, news, author):

    comments = [
        Comment.objects.create(
            news=news,
            author=author,
            text='Текст комментария',
            created=datetime.today() - timedelta(days=index)
        )
        for index in range(2)
    ]
    url = reverse('news:detail', args=(news.id,))

    # Act
    response = client.get(url)
    all_comments = response.context['news'].comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    sorted_dates = sorted(all_dates)

    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    url = reverse('news:detail', args=(news.id,))

    # Act
    response = client.get(url)

    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(reader_client, news):
    url = reverse('news:detail', args=(news.id,))

    # Act
    response = reader_client.get(url)

    assert 'form' in response.context
