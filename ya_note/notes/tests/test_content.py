from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


NOTE_SLUG = 'new-note'
NOTE_LIST_URL = reverse('notes:list')
NOTE_ADD_URL = reverse('notes:add')
NOTE_EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.admin_user = User.objects.create(username='admin_user')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.admin_client = Client()
        cls.admin_client.force_login(cls.admin_user)
        cls.note = Note.objects.create(
            text='Text',
            slug=NOTE_SLUG,
            author=cls.author,
        )

    def test_notes_list_for_author(self):
        response = self.author_client.get(NOTE_LIST_URL)
        object_list = response.context['object_list']
        self.assertTrue(self.note in object_list)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note.slug)

    def test_notes_list_for_admin_user(self):
        response = self.admin_client.get(NOTE_LIST_URL)
        object_list = response.context['object_list']
        self.assertFalse(self.note in object_list)

    def test_pages_contains_form(self):
        for url in (NOTE_ADD_URL, NOTE_EDIT_URL):
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
