from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            text='какой-то текст',
            slug='new-note',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        url = reverse('notes:list')
        users_note_in_list = (
            (self.author, True),
            (self.reader, False),
        )

        for user, note_in_list in users_note_in_list:
            self.client.force_login(user)

            with self.subTest(user=user):
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        self.client.force_login(self.author)
        urls_args = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )

        for name, args in urls_args:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
