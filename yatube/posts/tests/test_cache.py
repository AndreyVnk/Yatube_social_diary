from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post
from django.urls import reverse
from django.core.cache import cache

User = get_user_model()


class PostCacheTest(TestCase):
    """Класс проверки cache."""

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

    def test_cache(self):
        """Тест кеша с удалением поста."""

        response = self.client.get(reverse('posts:index'))
        posts_cache = response.content
        self.post.delete()
        self.assertEqual(
            Post.objects.all().count(),
            0
        )
        self.assertEqual(posts_cache, response.content)

        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotEqual(posts_cache, response.content)
