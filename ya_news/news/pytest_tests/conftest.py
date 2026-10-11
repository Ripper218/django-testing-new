from datetime import date, timedelta
import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

from .constants import NEWS_ON_PAGE


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
    today = date.today()
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст тестовой новости',
            date=today - timedelta(days=index),
        )
        for index in range(NEWS_ON_PAGE + 1)
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
        Comment.objects.filter(pk=item.pk).update(
            created=base_time + timedelta(minutes=index)
        )
    return list(Comment.objects.order_by('created'))


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=[news.pk])
