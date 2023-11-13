from notes.models import Note
from notes.forms import NoteForm
from notes.tests.base import BaseTest


class TestContent(BaseTest):
    """Tests for content-related functionality."""

    def test_notes_list_for_author(self):
        """Author's notes are displayed correctly on the notes list page."""
        response = self.author_client.get(self.NOTE_LIST_URL)
        object_list = response.context['object_list']
        self.assertTrue(self.note in object_list)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note.slug)

    def test_notes_list_for_admin_user(self):
        """Admin user doesn't see author's note on the notes list page."""
        self.assertEqual(Note.objects.count(), 1)
        response = self.admin_client.get(self.NOTE_LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 0)

    def test_pages_contains_form(self):
        """Certain pages contain the expected form."""
        for url in (self.NOTE_ADD_URL, self.NOTE_EDIT_URL):
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
