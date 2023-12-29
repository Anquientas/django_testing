import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects


# assert response.status_code != 200, response.context['form'].errors
@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, url):
    # Act
    response = client.get(reverse(url))

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_page_news_availability_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.id,))

    # Act
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args')),
    )
)
def test_pages_no_availability_for_anonymous_user(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'

    # Act
    response = client.get(url)

    assertRedirects(response, expected_url)


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
