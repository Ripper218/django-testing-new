from http import HTTPStatus

import pytest
from django.urls import reverse

from news.models import Comment
from .constants import WARNING_COMMENT_TEXT

FORM_DATA = {'text': 'Хороший комментарий', }

BAD_FORM_DATA = {'text': 'Ты редиска!', }


def test_anonymous_cannot_create_comment(client, news):
    url = reverse('news:detail', args=(news.pk,))
    comments_before = Comment.objects.count()

    response = client.post(url, data=FORM_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_before


def test_author_can_create_comment(author_client, author, news):
    existing_ids = set(Comment.objects.values_list('pk', flat=True))
    url = reverse('news:detail', args=(news.pk,))

    response = author_client.post(url, data=FORM_DATA)

    assert response.status_code == HTTPStatus.FOUND

    created = Comment.objects.exclude(pk__in=existing_ids)
    assert created.count() == 1

    comment = created.get()
    assert comment.news == news
    assert comment.author == author
    assert comment.text == FORM_DATA['text']


def test_comment_creation_redirects_to_comments_anchor(
    author_client, news,
):
    url = reverse('news:detail', args=(news.pk,))

    response = author_client.post(url, data=FORM_DATA)

    expected = reverse('news:detail', args=(news.pk,)) + '#comments'
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected


def test_bad_word_rejected(author_client, news):
    url = reverse('news:detail', args=(news.pk,))

    response = author_client.post(url, data=BAD_FORM_DATA)

    form = response.context['form']
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0
    assert form.errors['text'] == [
        WARNING_COMMENT_TEXT
    ]


def test_author_can_edit_own_comment(
    author_client,
    news,
    comment,
    detail_url
):
    url = reverse('news:edit', args=(comment.pk,))

    response = author_client.post(url, data=FORM_DATA)

    updated_comment = Comment.objects.get(pk=news.pk)
    assert response.url == detail_url + '#comments'
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == news


def test_author_can_delete_own_comment(comment, author_client,):
    url = reverse('news:delete', args=(comment.pk,))

    response = author_client.post(url)

    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_comment_delete_redirects_to_comments_anchor(
    author_client,
    comment,
    detail_url,
):
    url = reverse('news:delete', args=(comment.pk,))

    response = author_client.post(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url + '#comments'


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_reader_cannot_edit_or_delete_foreign_comment(
    reader_client,
    comment,
    name,
):
    url = reverse(name, args=(comment.pk,))
    comment_pk = comment.pk

    response = reader_client.post(url, data=FORM_DATA)

    assert response.status_code == HTTPStatus.NOT_FOUND

    saved = Comment.objects.get(pk=comment_pk)
    assert saved.text == comment.text
    assert saved.news.pk == comment.news.pk
    assert saved.author.pk == comment.author.pk
