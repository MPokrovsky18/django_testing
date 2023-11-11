import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(client, home_url, add_news_to_db):
    response = client.get(home_url)
    assert (
        len(response.context['object_list'])
        == settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_order(client, home_url, add_news_to_db):
    response = client.get(home_url)
    all_dates = [news.date for news in response.context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, news_url, add_comments_to_news):
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
    response = parametrized_client.get(news_url)
    assert (
        'form' in response.context
        and isinstance(response.context['form'], CommentForm)
    ) == has_form_result
