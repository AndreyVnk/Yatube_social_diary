from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostCacheTest(TestCase):
    """Класс проверки cache."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="title",
            slug="slug",
            description="description",
        )
        cls.post = Post.objects.create(
            author=cls.user, text="text", group=cls.group
        )

    def test_cache(self):
        """Тест кеша с удалением поста."""

        response = self.client.get(reverse("posts:index"))
        posts_cache = response.content
        # delete post
        self.post.delete()
        self.assertEqual(Post.objects.all().count(), 0)
        self.assertEqual(posts_cache, response.content)
        # clear cash\
        cache.clear()
        response = self.client.get(reverse("posts:index"))
        self.assertNotEqual(posts_cache, response.content)
