from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class BaseTest(TestCase):
    """Base test class for other test classes."""

    NOTE_SLUG = 'new-note'
    LOGIN_URL = reverse('users:login')
    LOGOUT_URL = reverse('users:logout')
    SIGNUP_URL = reverse('users:signup')
    HOME_URL = reverse('notes:home')
    NOTE_LIST_URL = reverse('notes:list')
    NOTE_ADD_URL = reverse('notes:add')
    SUCCESS_URL = reverse('notes:success')
    NOTE_DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))
    NOTE_EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
    NOTE_DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the base test class.
        - Creates an author user.
        - Creates an admin user.
        - Sets up client instances for the author and admin users.
        - Creates a sample note for testing.
        """
        cls.author = User.objects.create(username='author')
        cls.admin_user = User.objects.create(username='admin_user')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.admin_client = Client()
        cls.admin_client.force_login(cls.admin_user)
        cls.note = Note.objects.create(
            text='какой-то текст',
            slug=cls.NOTE_SLUG,
            author=cls.author,
        )
