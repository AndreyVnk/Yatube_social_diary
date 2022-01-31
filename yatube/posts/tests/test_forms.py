import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    """Класс проверки Forms."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(username="auth")
        cls.second_user = User.objects.create_user(username="second_auth")
        cls.group = Group.objects.create(
            title="title",
            slug="slug",
            description="description",
        )
        small_image = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=small_image, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            author=cls.first_user, text="text", group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.first_user,
            text="comment",
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.first_authorized_client = Client()
        self.first_authorized_client.force_login(self.first_user)
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(self.second_user)

    def test_post_create_guest(self):
        """Создание поста с изобжаением
        неавторизованным пользователем.
        """

        posts_count = Post.objects.count()
        form_data = {"text": "Тестовый текст", "image": self.uploaded}
        self.client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_create_auth(self):
        """Создание поста с изображением
        авторизованным пользователем.
        """

        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.id,
            "image": self.uploaded,
        }
        response = self.first_authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        new_post = Post.objects.latest("id")
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(new_post.text, form_data["text"])
        self.assertEqual(new_post.group.id, form_data["group"])
        self.assertIn(form_data["image"].name, new_post.image.name)
        self.assertRedirects(
            response,
            reverse(
                "posts:profile", kwargs={"username": self.first_user.username}
            ),
        )

    def test_post_edit_guest(self):
        """Редактирование поста неавторизованным пользователем."""

        form_data = {
            "text": "Измененный текст",
        }
        self.client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        edit_post = Post.objects.get(id=self.post.id)

        self.assertNotEqual(edit_post.text, form_data["text"])

    def test_post_edit_another_user(self):
        """Редактирование поста другим пользователем."""

        form_data = {
            "text": "Измененный текст",
        }
        self.second_authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        edit_post = Post.objects.get(id=self.post.id)

        self.assertNotEqual(edit_post.text, form_data["text"])

    def test_post_edit_author(self):
        """Редактирование поста автором."""

        posts_count = Post.objects.count()
        form_data = {
            "text": "Измененный текст",
            "group": self.group.id,
        }
        response = self.first_authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        edit_post = Post.objects.get(id=self.post.id)

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edit_post.text, form_data["text"])
        self.assertEqual(edit_post.group.id, form_data["group"])
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
        )

    def test_comment_create_guest(self):
        """Создание комментария неавторизованным пользователем."""

        comments_count = Comment.objects.count()
        form_data = {
            "text": "Коммент #2",
        }
        self.client.post(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": self.post.id},
            ),
            data=form_data,
            follow=True,
        )

        self.assertEqual(Comment.objects.count(), comments_count)

    def test_comment_create_auth(self):
        """Создание комментария авторизованным пользователем."""

        comments_count = Comment.objects.count()
        form_data = {
            "text": "Коммент #2",
        }
        response = self.first_authorized_client.post(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": self.post.id},
            ),
            data=form_data,
            follow=True,
        )
        comment = Comment.objects.latest("id")
        self.assertEqual(comment.post.id, self.post.id)
        self.assertEqual(comment.text, form_data["text"])
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
        )
