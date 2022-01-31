from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    """Класс проверки models."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user, text="Текст поста", group=cls.group
        )

    def test_model_post_have_correct_text(self):
        """В поле __str__  объекта post записано значение поля post.text."""

        expected_object_name = self.post.text[:15]
        self.assertEqual(expected_object_name, str(self.post))

    def test_model_group_have_correct_title(self):
        """В поле __str__  объекта group записано значение поля group.title."""

        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(self.group))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""

        field_verboses = {
            "text": "Текст поста",
            "pub_date": "Дата публикации",
            "author": "Автор",
            "group": "Группа",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value,
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""

        field_help_texts = {
            "text": "Введите текст поста",
            "group": "Выберите группу",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value
                )
