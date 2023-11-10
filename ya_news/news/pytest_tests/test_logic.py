from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_id_for_args):
    comment_text = 'New Comment'
    url = reverse('news:detail', args=news_id_for_args)
    response = client.post(url, data={'text': comment_text})
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news):
    comment_text = 'New Comment'
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data={'text': comment_text})
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == comment_text
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news_id_for_args):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
            response,
            form='form',
            field='text',
            errors=WARNING
        )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, comment, news_id_for_args):
    new_comment_data = {'text': 'Edit comment'}
    edit_url = reverse('news:edit', args=(comment.id,))
    detail_url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(edit_url, data=new_comment_data)
    assertRedirects(response, f'{detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == new_comment_data['text']


def test_user_cant_edit_comment_of_another_user(admin_client, comment):
    new_comment_data = {'text': 'Edit comment'}
    edit_url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(edit_url, data=new_comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == Comment.objects.get(id=comment.id).text


def test_author_can_delete_comment(author_client, comment, news_id_for_args):
    delete_url = reverse('news:delete', args=(comment.id,))
    detail_url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(delete_url)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
