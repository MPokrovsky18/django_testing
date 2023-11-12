from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING
from notes.tests.base import BaseTest


FORM_DATA = {
    'title': 'Новый заголовок',
    'text': 'Новый текст',
    'slug': BaseTest.NOTE_SLUG,
}


class TestNoteCreation(BaseTest):
    """Tests for creating new notes."""

    def test_anonymous_user_cant_create_note(self):
        """An anonymous user cannot create a note."""
        start_nout_count = Note.objects.count()
        response = self.client.post(self.NOTE_ADD_URL, data=FORM_DATA)
        expected_url = f'{self.LOGIN_URL}?next={self.NOTE_ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), start_nout_count)

    def test_user_can_create_note(self):
        """An authenticated user can successfully create a note."""
        Note.objects.all().delete()
        self.assertEqual(Note.objects.count(), 0)
        response = self.author_client.post(self.NOTE_ADD_URL, data=FORM_DATA)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, FORM_DATA['title'])
        self.assertEqual(new_note.text, FORM_DATA['text'])
        self.assertEqual(new_note.slug, FORM_DATA['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_not_unique_slug(self):
        """Test creating a note with a non-unique slug."""
        start_note_count = Note.objects.count()
        response = self.author_client.post(self.NOTE_ADD_URL, data=FORM_DATA)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.NOTE_SLUG + WARNING)
        )
        self.assertEqual(Note.objects.count(), start_note_count)

    def test_empty_slug(self):
        """Test creating a note with an empty slug."""
        Note.objects.all().delete()
        self.assertEqual(Note.objects.count(), 0)
        new_form_data = FORM_DATA.copy()
        new_form_data.pop('slug')
        response = self.author_client.post(
            self.NOTE_ADD_URL, data=new_form_data
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(FORM_DATA['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.title, FORM_DATA['title'])
        self.assertEqual(new_note.text, FORM_DATA['text'])
        self.assertEqual(new_note.author, self.author)


class TestNoteEditDelete(BaseTest):
    """Tests for editing and deleting notes."""

    def test_author_can_edit_note(self):
        """The author of a note can successfully edit their own note."""
        start_note_count = Note.objects.count()
        self.assertEqual(start_note_count, 1)
        response = self.author_client.post(self.NOTE_EDIT_URL, FORM_DATA)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), start_note_count)
        edit_note = Note.objects.get()
        self.assertEqual(edit_note.text, FORM_DATA['text'])
        self.assertEqual(edit_note.title, FORM_DATA['title'])
        self.assertEqual(edit_note.slug, FORM_DATA['slug'])
        self.assertEqual(edit_note.author, self.author)

    def test_other_user_cant_edit_note(self):
        """Another user cannot edit someone else's note."""
        start_note_count = Note.objects.count()
        self.assertEqual(start_note_count, 1)
        response = self.admin_client.post(self.NOTE_EDIT_URL, FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), start_note_count)
        edit_note = Note.objects.get()
        self.assertFalse(edit_note.text == FORM_DATA['text'])
        self.assertFalse(edit_note.title == FORM_DATA['title'])
        self.assertEqual(edit_note.slug, FORM_DATA['slug'])
        self.assertEqual(edit_note.author, self.author)

    def test_author_can_delete_note(self):
        """The author of a note can successfully delete their own note."""
        start_note_count = Note.objects.count()
        response = self.author_client.post(self.NOTE_DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(start_note_count - Note.objects.count(), 1)

    def test_other_user_cant_delete_note(self):
        """Another user cannot delete someone else's note."""
        start_note_count = Note.objects.count()
        response = self.admin_client.post(self.NOTE_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.count(), start_note_count)
