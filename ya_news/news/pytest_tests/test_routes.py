from http import HTTPStatus

import pytest


pytestmark = pytest.mark.django_db


def test_status_codes(
    subtests,
    client,
    author_client,
    reader_client,
    home_url,
    login_url,
    signup_url,
    detail_url,
    edit_url,
    delete_url,
    logout_url,
):
    cases = (
        (home_url, client, 'get', HTTPStatus.OK),
        (login_url, client, 'get', HTTPStatus.OK),
        (signup_url, client, 'get', HTTPStatus.OK),
        (detail_url, client, 'get', HTTPStatus.OK),
        (edit_url, author_client, 'get', HTTPStatus.OK),
        (delete_url, author_client, 'get', HTTPStatus.OK),
        (edit_url, reader_client, 'get', HTTPStatus.NOT_FOUND),
        (delete_url, reader_client, 'get', HTTPStatus.NOT_FOUND),
        (edit_url, client, 'get', HTTPStatus.FOUND),
        (delete_url, client, 'get', HTTPStatus.FOUND),
        (logout_url, client, 'get', HTTPStatus.METHOD_NOT_ALLOWED),
        (logout_url, author_client, 'post', HTTPStatus.OK),
    )

    for url, client_item, method, expected_status in cases:
        with subtests.test(url=url, method=method):
            response = getattr(client_item, method)(url)

            assert response.status_code == expected_status


def test_redirects(
    subtests,
    client,
    edit_url,
    delete_url,
    edit_redirect_url,
    delete_redirect_url,
):
    cases = (
        (edit_url, edit_redirect_url),
        (delete_url, delete_redirect_url),
    )

    for url, expected_url in cases:
        with subtests.test(url=url):
            response = client.get(url)

            assert response.url == expected_url
