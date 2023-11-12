from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


NOTE_SLUG = 'new-note'
HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
NOTE_LIST_URL = reverse('notes:list')
NOTE_ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
NOTE_DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))
NOTE_EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
NOTE_DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.admin_user = User.objects.create(username='admin_user')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.admin_client = Client()
        cls.admin_client.force_login(cls.admin_user)
        cls.note = Note.objects.create(
            text='какой-то текст',
            slug=NOTE_SLUG,
            author=cls.author,
        )
        cls.urls = (
            HOME_URL,
            NOTE_LIST_URL,
            NOTE_ADD_URL,
            SUCCESS_URL,
            NOTE_DETAIL_URL,
            NOTE_EDIT_URL,
            NOTE_DELETE_URL,
            LOGIN_URL,
            LOGOUT_URL,
            SIGNUP_URL,
        )

    def test_pages_availability_for_author(self):
        for page_url in self.urls:
            with self.subTest(name=page_url):
                response = self.author_client.get(page_url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_not_author(self):
        for page_url in self.urls:
            with self.subTest(name=page_url):
                response = self.admin_client.get(page_url)
                if page_url in (NOTE_DETAIL_URL, NOTE_EDIT_URL, NOTE_DELETE_URL,):
                    self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_anonymous_user(self):
        for page_url in self.urls:
            with self.subTest(name=page_url):
                response = self.client.get(page_url)

                if page_url in (
                    HOME_URL,
                    LOGIN_URL,
                    LOGOUT_URL,
                    SIGNUP_URL,
                ):
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertRedirects(response, f'{LOGIN_URL}?next={page_url}')
