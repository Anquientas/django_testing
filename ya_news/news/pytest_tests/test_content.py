from django.conf import settings

from news.forms import CommentForm


def test_count_news_on_home_page(client, news_home_url, several_news):
    assert len(
        client.get(news_home_url).context['object_list']
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_sort_news_on_home_page(client, news_home_url, several_news):
    all_dates = [
        news.date for news in client.get(news_home_url).context['object_list']
    ]
    assert all_dates == sorted(all_dates, reverse=True)


def test_sort_comments(client, news_detail_url, several_comments):
    all_dates = [
        comment.created
        for comment
        in client.get(news_detail_url).context['news'].comment_set.all()
    ]
    assert all_dates == sorted(all_dates)


def test_anonymous_client_has_no_form(client, news_detail_url):
    assert 'form' not in client.get(news_detail_url).context


def test_authorized_client_has_form(client_reader, news_detail_url):
    context = client_reader.get(news_detail_url).context
    assert 'form' in context
    assert isinstance(context['form'], CommentForm)
