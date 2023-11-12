from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING


NOTE_SLUG = 'new-note'
LOGIN_URL = reverse('users:login')
NOTE_LIST_URL = reverse('notes:list')
NOTE_ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
NOTE_EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
NOTE_DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))


User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='new_user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': NOTE_SLUG,
        }

    def test_anonymous_user_cant_create_note(self):
        start_nout_count = Note.objects.count()
        response = self.client.post(NOTE_ADD_URL, data=self.form_data)
        expected_url = f'{LOGIN_URL}?next={NOTE_ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), start_nout_count)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        self.assertEqual(Note.objects.count(), 0)
        response = self.auth_client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_not_unique_slug(self):
        Note.objects.create(
            title=self.form_data['title'],
            text=self.form_data['text'],
            slug=self.form_data['slug'],
            author=self.user,
        )
        start_note_count = Note.objects.count()
        response = self.auth_client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(NOTE_SLUG + WARNING)
        )
        self.assertEqual(Note.objects.count(), start_note_count)

    def test_empty_slug(self):
        Note.objects.all().delete()
        self.assertEqual(Note.objects.count(), 0)
        self.form_data.pop('slug')
        response = self.auth_client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.user)


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            text='какой-то текст',
            slug=NOTE_SLUG,
            author=cls.author,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': cls.note.title,
            'text': 'any text',
            'slug': NOTE_SLUG,
        }

    def test_author_can_edit_note(self):
        start_note_count = Note.objects.count()
        self.assertEqual(start_note_count, 1)
        response = self.author_client.post(NOTE_EDIT_URL, self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), start_note_count)
        edit_note = Note.objects.get()
        self.assertEqual(edit_note.text, self.form_data['text'])
        self.assertEqual(edit_note.title, self.form_data['title'])
        self.assertEqual(edit_note.slug, self.form_data['slug'])
        self.assertEqual(edit_note.author, self.author)

    def test_other_user_cant_edit_note(self):
        start_note_count = Note.objects.count()
        self.assertEqual(start_note_count, 1)
        response = self.reader_client.post(NOTE_EDIT_URL, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), start_note_count)
        edit_note = Note.objects.get()
        self.assertFalse(edit_note.text == self.form_data['text'])

    def test_author_can_delete_note(self):
        start_note_count = Note.objects.count()
        response = self.author_client.post(NOTE_DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(start_note_count - Note.objects.count(), 1)

    def test_other_user_cant_delete_note(self):
        start_note_count = Note.objects.count()
        response = self.reader_client.post(NOTE_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.count(), start_note_count)
