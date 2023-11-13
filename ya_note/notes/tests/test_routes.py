from http import HTTPStatus

from notes.tests.base import BaseTest


class TestRoutes(BaseTest):
    """Tests for the availability of different routes."""

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for route availability tests.
        - Creates routes list.
        """
        super().setUpTestData()
        cls.urls = (
            cls.HOME_URL,
            cls.NOTE_LIST_URL,
            cls.NOTE_ADD_URL,
            cls.SUCCESS_URL,
            cls.NOTE_DETAIL_URL,
            cls.NOTE_EDIT_URL,
            cls.NOTE_DELETE_URL,
            cls.LOGIN_URL,
            cls.LOGOUT_URL,
            cls.SIGNUP_URL,
        )

    def test_pages_availability_for_author(self):
        """Check if authorized author can access various pages."""
        for page_url in self.urls:
            with self.subTest(name=page_url):
                response = self.author_client.get(page_url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_not_author(self):
        """Check if authorized non-author can access various pages."""
        pages_without_availability = (
            self.NOTE_DETAIL_URL,
            self.NOTE_EDIT_URL,
            self.NOTE_DELETE_URL,
        )

        for page_url in self.urls:
            with self.subTest(name=page_url):
                response = self.admin_client.get(page_url)
                if page_url in pages_without_availability:
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND
                    )
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_anonymous_user(self):
        """Check if anonymous user can access various pages."""
        pages_availability_for_anonymus = (
            self.HOME_URL,
            self.LOGIN_URL,
            self.LOGOUT_URL,
            self.SIGNUP_URL,
        )

        for page_url in self.urls:
            with self.subTest(name=page_url):
                response = self.client.get(page_url)

                if page_url in pages_availability_for_anonymus:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertRedirects(
                        response, f'{self.LOGIN_URL}?next={page_url}'
                    )
