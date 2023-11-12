from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Fixture for creating an author user."""
    return django_user_model.objects.create(username='author')


@pytest.fixture
def author_client(author, client):
    """Fixture for creating an authorized client with an author user."""
    client.force_login(author)
    return client


@pytest.fixture
def news():
    """Fixture for creating a news instance."""
    return News.objects.create(title='Title', text='Text')


@pytest.fixture
def comment(news, author):
    """Fixture for creating a comment instance."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Comment Text',
    )


@pytest.fixture
def add_news_to_db():
    """Fixture for adding multiple news instances to the database."""
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'News {index}',
            text='Text',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def add_comments_to_news(news, author):
    """
    Fixture for adding multiple comments
    to a news instance in the database.
    """
    Comment.objects.bulk_create(
        Comment(
            news=news, author=author, text=f'Text {index}',
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def home_url():
    """Fixture for getting the URL for the home page."""
    return reverse('news:home')


@pytest.fixture
def news_url(news):
    """Fixture for getting the URL for the news detail page."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def login_url():
    """Fixture for getting the URL for the user login page."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """Fixture for getting the URL for the user logout page."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """Fixture for getting the URL for the user signup page."""
    return reverse('users:signup')


@pytest.fixture
def edit_url(comment):
    """Fixture for getting the URL for editing a comment."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    """Fixture for getting the URL for deleting a comment."""
    return reverse('news:delete', args=(comment.id,))
