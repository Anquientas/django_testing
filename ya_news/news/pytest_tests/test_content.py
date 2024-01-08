from django.conf import settings
import pytest


NEWS_DETAIL = pytest.lazy_fixture('news_detail')
NEWS_HOME = pytest.lazy_fixture('news_home')


@pytest.mark.parametrize('url', [NEWS_HOME])
def test_count_news_on_home_page(client_anonymous, url, several_news):
    assert len(
        client_anonymous.get(url).context['object_list']
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.parametrize('url', [NEWS_HOME])
def test_sort_news_on_home_page(client_anonymous, url, several_news):
    # Act
    all_dates = [
        news.date for news in client_anonymous.get(url).context['object_list']
    ]

    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.parametrize('url', [NEWS_DETAIL])
def test_sort_comments(client_anonymous, url, several_comments):
    # Act
    all_dates = [
        comment.created
        for comment
        in client_anonymous.get(url).context['news'].comment_set.all()
    ]

    assert all_dates == sorted(all_dates)


@pytest.mark.parametrize('url', [NEWS_DETAIL])
def test_anonymous_client_has_no_form(client_anonymous, url):
    assert 'form' not in client_anonymous.get(url).context


@pytest.mark.parametrize('url', [NEWS_DETAIL])
def test_authorized_client_has_form(client_reader, url):
    assert 'form' in client_reader.get(url).context
    assert 'text' in client_reader.get(url).context['form'].fields
    assert 'title' not in client_reader.get(url).context['form'].fields
    assert 'date' not in client_reader.get(url).context['form'].fields
