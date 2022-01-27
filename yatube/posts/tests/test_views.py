import shutil
import tempfile
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Comment, Group, Post
from posts.utils import paginator_page_2

from yatube.settings import PAGE_SIZE_PAGINATOR

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):
    """Класс проверки views."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(username='auth')
        cls.second_user = User.objects.create_user(username='second_auth')
        cls.first_group = Group.objects.create(
            title='first_title',
            slug='first_slug',
            description='first_description',
        )
        cls.second_group = Group.objects.create(
            title='second_title',
            slug='second_slug',
            description='second_description',
        )
        cls.third_group = Group.objects.create(
            title='third_title',
            slug='third_slug',
            description='third_description',
        )
        small_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_image,
            content_type='image/gif'
        )
        for _ in range(7):
            cls.post = Post.objects.create(
                author=cls.first_user,
                text='text',
                group=cls.first_group,
            )
        for _ in range(11):
            Post.objects.create(
                author=cls.second_user,
                text='text',
                group=cls.second_group,
            )
        # create last post with picture
        time.sleep(1 / 1000)
        cls.post_image = Post.objects.create(
            author=cls.second_user,
            text='text',
            group=cls.second_group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post_image,
            author=cls.second_user,
            text='comment',

        )
        cls.check_post = Post.objects.filter(
            author=cls.second_user,
            text='text',
            group=cls.second_group
        )[0]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTest.first_user)

    def test_urls_guest_client_uses_correct_template(self):
        """Неавторизованный пользователь:
        URL-адрес использует соответствующий шаблон.
        """

        templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': self.first_group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.first_user.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_authorized_client_uses_correct_template(self):
        """Авторизованный пользователь:
        URL-адрес использует соответствующий шаблон.
        """

        templates_url_names = {
            'posts/create_post.html': (
                reverse('posts:post_create'),
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.id}
                ),
            )
        }
        for template, address in templates_url_names.items():
            for url in address:
                with self.subTest(url=url):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, template)

    def test_posts_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом - список постов
        + тест паджинатора + тест поста с изображением.
        """
        posts_count = Post.objects.all().count()
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']), PAGE_SIZE_PAGINATOR
        )

        index_page_pict = response.context['page_obj'][0].image
        self.assertEqual(index_page_pict, self.post_image.image)

        response = self.client.get(reverse('posts:index') + '?page=2')
        paginator_page_2(self, response, posts_count)

    def test_posts_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом -
        список постов отфильтрованных по группе
        + тест паджинатора + тест поста с изображением.
        """

        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.second_group.slug}
            )
        )
        group_group_list_page = response.context['group']
        title_group_list_page = response.context['title']
        group_list_page_pict = response.context['page_obj'][0].image

        posts_count = Post.objects.filter(
            group=self.second_group
        ).count()
        self.assertEqual(group_list_page_pict, self.post_image.image)
        self.assertEqual(group_group_list_page, self.second_group)
        self.assertEqual(
            title_group_list_page,
            f'Записи сообщества {self.second_group.title}'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            PAGE_SIZE_PAGINATOR
        )

        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.second_group.slug}
            ) + '?page=2'
        )
        paginator_page_2(self, response, posts_count)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом -
        спиок постов отфильтрованных по пользователю
        + тест паджинатора + тест поста с изображением.
        """
        posts_count = Post.objects.filter(
            author=self.second_user
        ).count()
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.second_user.username}
            )
        )
        profile_page_pict = response.context['page_obj'][0].image

        self.assertEqual(profile_page_pict, self.post_image.image)
        self.assertEqual(
            len(response.context['page_obj']),
            PAGE_SIZE_PAGINATOR
        )

        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.second_user.username}
            ) + '?page=2'
        )
        paginator_page_2(self, response, posts_count)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом
         + тест поста с изображением."""

        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post_detail_page_text = response.context['post'].text
        self.assertEqual(post_detail_page_text, 'text')

        response = self.client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post_image.id}
            )
        )
        post_detail_page_pict = response.context['post'].image
        self.assertEqual(post_detail_page_pict, 'posts/small.gif')

    def test_post_create_show_correct_form(self):
        """Шаблон post_create сформирован с правильной формой."""

        response = self.authorized_client.get(reverse('posts:post_create'))
        form_create_page = response.context['form']
        self.assertIsInstance(form_create_page, PostForm)

    def test_post_edit_show_correct_form(self):
        """Шаблон post_edit сформирован с правильной формой."""

        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_edit_page = response.context['form']
        is_edit_edit_page = response.context['is_edit']
        self.assertIsInstance(form_edit_page, PostForm)
        self.assertTrue(is_edit_edit_page)

    def test_group_list_page_another_group_not_contains_post(self):
        """Проверка, что пост не попал в другую группу."""

        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.third_group.slug}
            )
        )
        self.assertNotIn(
            self.check_post,
            response.context['page_obj']
        )

    def test_index_page_contains_post(self):
        """Проверка, что если при создании поста указать группу,
        пост появляется на главной странице сайта.
        """

        response = self.client.get(reverse('posts:index'))
        self.assertIn(
            self.check_post,
            response.context['page_obj']
        )

    def test_group_list_page_contains_post(self):
        """Проверка, что если при создании поста указать группу,
        пост появляется на странице выбранной группы.
        """

        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.second_group.slug}
            )
        )
        self.assertIn(
            self.check_post,
            response.context['page_obj']
        )

    def test_profile_page_contains_post(self):
        """Проверка, что если при создании поста указать группу,
        пост появляется в профайле пользователя.
        """

        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.second_user.username}
            )
        )
        self.assertIn(
            self.check_post,
            response.context['page_obj']
        )

    def test_post_image_contains_comment(self):
        """Проверка, что комментарий к посту
        появляется под постом.
        """

        response = self.client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post_image.id}
            )
        )
        self.assertIn(
            self.comment,
            response.context['comments']
        )
