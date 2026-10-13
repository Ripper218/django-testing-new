from http import HTTPStatus

import pytest


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ('url_fixture', 'client_fixture', 'method', 'expected_status'),
    (
        ('home_url', 'client', 'get', HTTPStatus.OK),
        ('login_url', 'client', 'get', HTTPStatus.OK),
        ('signup_url', 'client', 'get', HTTPStatus.OK),
        ('detail_url', 'client', 'get', HTTPStatus.OK),
        ('edit_url', 'author_client', 'get', HTTPStatus.OK),
        ('delete_url', 'author_client', 'get', HTTPStatus.OK),
        ('edit_url', 'reader_client', 'get', HTTPStatus.NOT_FOUND),
        ('delete_url', 'reader_client', 'get', HTTPStatus.NOT_FOUND),
        ('logout_url', 'client', 'get', HTTPStatus.METHOD_NOT_ALLOWED),
        ('logout_url', 'author_client', 'post', HTTPStatus.OK),
    ),
)
def test_status_codes(
    request, url_fixture, client_fixture, method, expected_status,
):
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)

    response = getattr(client, method)(url)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ('url_fixture', 'client_fixture'),
    (
        ('edit_url', 'client'),
        ('delete_url', 'client'),
    ),
)
def test_redirects(request, url_fixture, client_fixture, login_url):
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{login_url}?next={url}'
