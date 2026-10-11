from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:signup'),
)
def test_public_pages_are_available(client, name, db):
    url = reverse(name)

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


def test_detail_available_to_anonymous(client, news, detail_url):
    response = client.get(detail_url)

    assert response.status_code == HTTPStatus.OK
    assert response.context['news'] == news


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_comment_pages_available_to_author(
    comment,
    author_client,
    name,
):
    url = reverse(name, args=(comment.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_comment_pages_are_unavailable_to_reader(
    comment,
    reader_client,
    name,
):
    url = reverse(name, args=(comment.pk,))
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_anonymous_user_is_redirected_to_login(
    comment,
    client,
    name,
):
    url = reverse(name, args=(comment.pk,))
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


def test_logout_accepts_post_request(
    author_client,
):
    url = reverse('users:logout')

    response = author_client.post(url)

    assert response.status_code == HTTPStatus.OK
    assert '_auth_user_id' not in author_client.session


def test_logout_rejects_get_request(client):
    url = reverse('users:logout')

    response = client.get(url)

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
