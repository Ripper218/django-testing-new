from http import HTTPStatus

import pytest


pytestmark = pytest.mark.django_db


def test_status_codes(subtests, status_cases):
    for url, client, method, expected_status in status_cases:
        with subtests.test(url=url, method=method):
            response = getattr(client, method)(url)

            assert response.status_code == expected_status


def test_redirects(subtests, redirect_cases):
    for url, client, expected_url in redirect_cases:
        with subtests.test(url=url):
            response = client.get(url)

            assert response.status_code == HTTPStatus.FOUND
            assert response.url == expected_url
