import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(client, home_url, add_news_to_db):
    """Test that the home page displays the correct number of news."""
    response = client.get(home_url)
    assert (
        len(response.context['object_list'])
        == settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_order(client, home_url, add_news_to_db):
    """Test that the news on the home page are ordered by date."""
    response = client.get(home_url)
    all_dates = [news.date for news in response.context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, news_url, add_comments_to_news):
    """Test that comments on the news detail page are ordered by date."""
    response = client.get(news_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments_dates = [
        comment.created for comment in news.comment_set.all()
    ]
    assert all_comments_dates == sorted(all_comments_dates)


@pytest.mark.parametrize(
    'parametrized_client, has_form_result',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_client_has_form(
    parametrized_client, has_form_result, news_url
):
    """Test that the client context includes a CommentForm."""
    response = parametrized_client.get(news_url)
    assert (
        'form' in response.context
        and isinstance(response.context['form'], CommentForm)
    ) == has_form_result
