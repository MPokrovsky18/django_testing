from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='author')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='Title', text='Text')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Comment Text',
    )


@pytest.fixture
def news_id_for_args(news):
    return news.id,


@pytest.fixture
def news_object_list(client):
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'News {index}',
            text='Text',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    response = client.get(reverse('news:home'))

    return response.context['object_list']


@pytest.fixture
def add_comments_to_news(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Text {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
