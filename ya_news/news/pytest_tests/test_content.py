from http import HTTPStatus

from django.urls import reverse

from news.forms import CommentForm

from .constants import NEWS_ON_PAGE


def test_news_count_on_page_is_limited(
    more_news,
    author_client,
):
    response = author_client.get(reverse('news:home'))
    object_list = response.context['object_list']

    assert len(object_list) == NEWS_ON_PAGE


def test_news_are_sorted_newest_first(more_news, author_client):
    response = author_client.get(reverse('news:home'))

    object_list = list(response.context['object_list'])
    expected_notes = list(more_news)[:NEWS_ON_PAGE]

    assert object_list == expected_notes


def test_comments_are_sorted_oldest_first(
    several_comments, author_client, detail_url,
):
    response = author_client.get(detail_url)
    comments = list(response.context['news'].comment_set.all())
    expected_comments = list(several_comments)

    assert comments == expected_comments


def test_comment_form_not_passed_to_anonymous(client, news):
    url = reverse('news:detail', args=(news.pk,))

    response = client.get(url)

    assert 'form' not in response.context


def test_comment_form_passed_to_author(author_client, news):
    url = reverse('news:detail', args=(news.pk,))

    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
