from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


pytestmark = pytest.mark.django_db


COMMENT_TEXT = 'New Comment'
EDIT_COMMENT_TEXT = 'Edit Comment'


def test_anonymous_user_cant_create_comment(client, news_url, login_url):
    """An anonymous user cannot create a comment."""
    start_comment_count = Comment.objects.count()
    response = client.post(news_url, data={'text': COMMENT_TEXT})
    expected_url = f'{login_url}?next={news_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == start_comment_count


def test_user_can_create_comment(author_client, author, news_url, news):
    """An authenticated user can successfully create a comment."""
    start_comment_set = set(Comment.objects.all())
    response = author_client.post(news_url, data={'text': COMMENT_TEXT})
    assertRedirects(response, f'{news_url}#comments')
    only_new_comments_set = (
        set(Comment.objects.all()).difference(start_comment_set)
    )
    assert len(only_new_comments_set) == 1
    comment = only_new_comments_set.pop()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news_url):
    """A user cannot use prohibited words in a comment."""
    start_comment_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(news_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == start_comment_count


def test_author_can_edit_comment(
        author_client, author, news, comment, news_url, edit_url
):
    """The author of a comment can successfully edit their own comment."""
    start_comment_count = Comment.objects.count()
    response = author_client.post(edit_url, data={'text': EDIT_COMMENT_TEXT})
    assertRedirects(response, f'{news_url}#comments')
    assert Comment.objects.count() == start_comment_count
    edit_comment = Comment.objects.get(id=comment.id)
    assert edit_comment.text == EDIT_COMMENT_TEXT
    assert edit_comment.news == news
    assert edit_comment.author == author


def test_user_cant_edit_comment_of_another_user(
        admin_client, comment, edit_url
):
    """A user cannot edit a comment authored by someone else."""
    start_comment_count = Comment.objects.count()
    response = admin_client.post(edit_url, data={'text': EDIT_COMMENT_TEXT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == start_comment_count
    edit_comment = Comment.objects.get(id=comment.id)
    assert edit_comment.text == comment.text
    assert edit_comment.news == comment.news
    assert edit_comment.author == comment.author


def test_author_can_delete_comment(author_client, news_url, delete_url):
    """The author of a comment can successfully delete their own comment."""
    start_comment_count = Comment.objects.count()
    response = author_client.post(delete_url)
    assertRedirects(response, f'{news_url}#comments')
    assert start_comment_count - Comment.objects.count() == 1


def test_user_cant_delete_comment_of_another_user(admin_client, delete_url):
    """A user cannot delete a comment authored by someone else."""
    start_comment_count = Comment.objects.count()
    response = admin_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == start_comment_count
