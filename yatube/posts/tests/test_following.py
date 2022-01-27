from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post, Follow
from django.urls import reverse

User = get_user_model()


class PostSubsTest(TestCase):
    """Класс проверки Subcribes."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(username='auth')
        cls.second_user = User.objects.create_user(username='auth_2')
        cls.third_user = User.objects.create_user(username='auth_3')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description',
        )
        cls.post_sec_us = Post.objects.create(
            author=cls.second_user,
            text='text',
            group=cls.group
        )
        cls.post_thd_us = Post.objects.create(
            author=cls.third_user,
            text='text',
            group=cls.group
        )
        Follow.objects.create(
            user=cls.first_user,
            author=cls.second_user
        )

    def setUp(self):
        self.first_authorized_client = Client()
        self.first_authorized_client.force_login(self.first_user)
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(self.second_user)

    def test_following_auth(self):
        """Subcribe by auth user."""

        followers_count = Follow.objects.filter(user=self.first_user).count()
        self.first_authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.third_user.username}
            )
        )
        self.assertEqual(
            Follow.objects.filter(user=self.first_user).count(),
            followers_count + 1
        )

    def test_unfollowing_auth(self):
        """Unsubcribe by auth user."""

        followers_count = Follow.objects.filter(user=self.first_user).count()
        self.first_authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.second_user.username}
            )
        )
        self.assertEqual(
            Follow.objects.filter(user=self.first_user).count(),
            followers_count - 1
        )

    def test_post_available(self):
        """Post is available when user is subscribed."""

        response = self.first_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(
            self.post_sec_us,
            response.context['page_obj']
        )

    def test_post_unavailable(self):
        """Post is unavailable when user isn't subscribed."""

        response = self.first_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(
            self.post_thd_us,
            response.context['page_obj']
        )
