from http import HTTPStatus

from django.conf import settings

from news.forms import CommentForm


def test_news_count_on_page_is_limited(more_news, author_client, home_url):
    response = author_client.get(home_url)

    assert len(
        response.context['object_list']
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_are_sorted_newest_first(more_news, author_client, home_url):
    response = author_client.get(home_url)

    news_dates = [item.date for item in response.context['object_list']]

    assert news_dates == sorted(news_dates, reverse=True)


def test_comments_are_sorted_oldest_first(
    several_comments, author_client, detail_url,
):
    response = author_client.get(detail_url)

    created = [
        comment.created
        for comment in response.context['news'].comment_set.all()
    ]

    assert created == sorted(created)


def test_comment_form_not_passed_to_anonymous(client, news, detail_url):
    response = client.get(detail_url)

    assert 'form' not in response.context


def test_comment_form_passed_to_author(author_client, news, detail_url):
    response = author_client.get(detail_url)

    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
