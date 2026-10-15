from datetime import date, timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model, db):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model, db):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author, db):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, db):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Тестовая новость',
        text='Текст тестовой новости',
    )


@pytest.fixture
def more_news(db):
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст тестовой новости',
            date=date.today() - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(news, author, db):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария автора',
    )


@pytest.fixture
def several_comments(news, author, db):
    comments = Comment.objects.bulk_create(
        Comment(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )
        for index in range(3)
    )

    base_time = timezone.now()
    for index, item in enumerate(comments):
        item.created = base_time + timedelta(minutes=index)
        item.save(update_fields=['created'])


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def detail_url_comments(detail_url):
    return f'{detail_url}#comments'


@pytest.fixture
def edit_redirect_url(edit_url, login_url):
    return f'{login_url}?next={edit_url}'


@pytest.fixture
def delete_redirect_url(delete_url, login_url):
    return f'{login_url}?next={delete_url}'
