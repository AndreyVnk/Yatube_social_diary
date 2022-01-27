from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class StaticURLsTests(TestCase):
    """Класс проверки URLs."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='text',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_url_user_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""

        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_url_author_exists_at_desired_location(self):
        """Страница редактирования /posts/post_id/edit/ доступна автору."""

        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_template_urls_guest_exists_at_desired_loc(self):
        """URL-адрес возвращает соответсвующий
        статус для неавторизованного пользователя.
        """

        templates_url_names = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, template)

    def test_urls_client_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон
        для неавторизованного пользователя.
        """

        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'core/404.html': '/unexisting_page/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_auth_client_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон
        для авторизованного пользователя.
        """

        templates_url_names = {
            'posts/create_post.html': (
                '/create/', f'/posts/{self.post.id}/edit/'
            )
        }
        for template, address in templates_url_names.items():
            for url in address:
                with self.subTest(url=url):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, template)

    def test_post_create_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /create/ и
        /posts/post_id/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """

        templates_url_names = {
            '/auth/login/?next=': ('/create/', f'/posts/{self.post.id}/edit/')
        }

        for template, address in templates_url_names.items():
            for url in address:
                with self.subTest(url=url):
                    response = self.client.get(url, follow=True)
                    template_url = template + url
                    self.assertRedirects(response, template_url)
                    del template_url
