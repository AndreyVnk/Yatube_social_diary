from http import HTTPStatus

from django.test import TestCase


class AboutURLTests(TestCase):
    """Class Test URLS."""

    def test_about_url_exists(self):
        """Test URLS."""

        templates_urls_names = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for address, status in templates_urls_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, status)
