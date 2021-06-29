from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import User, Post, Group


class TaskURLTests(TestCase):
    User = get_user_model()

    @classmethod
    def setUp(self):
        super().setUpClass()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='AndreyG')
        self.user_2 = User.objects.create_user(username='TatianaK')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client.force_login(self.user_2)
        self.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        self.post = Post.objects.create(author=self.user,
                                        text='Тестовый текст поста',
                                        group=self.group)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_task_added_url_exists_at_desired_location(self):
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_homepage_url_exists_at_desired_location_authorize(self):
        response = self.authorized_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_task_group_url_exists_at_desired_location(self):
        response = self.authorized_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_task_detail_url_exists_at_desired_location_authorized(self):
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_profile_exists_at_desired_location_authorized(self):
        response = self.authorized_client.get(f'/{self.user.username}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_exists_at_desired_location_not_authorized(self):
        response = self.guest_client.get(f'/{self.user.username}/')
        self.assertEqual(response.status_code, 200)

    def test_post_exists_at_desired_location_authorized(self):
        response = self.authorized_client.get(
            f'/{self.user.username}/{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_post_exists_at_desired_location_not_authorized(self):
        response = self.guest_client.get(
            f'/{self.user.username}/{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_exists_at_desired_location_not_authorized(self):
        response = self.guest_client.get(
            f'/{self.user.username}/{self.post.id}/edit/')
        self.assertNotEqual(response.status_code, 200)

    def test_post_edit_exists_at_desired_location_for_author(self):
        response = self.guest_client.get(
            f'/{self.user.username}/{self.post.id}/edit/')
        self.assertNotEqual(response.status_code, 200)

    def test_post_edit_not_available_for_other_user(self):
        response = self.guest_client.get(
            f'/{self.user_2.username}/{self.post.id}/edit/')
        self.assertNotEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'misc/index.html': '/',
            'posts/group.html': '/group/test-slug/',
            'posts/new.html': '/new/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(adress=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_for_edit(self):
        response = self.authorized_client.get(
            f'/{self.user.username}/{self.post.id}/')
        self.assertTemplateUsed(response, 'posts/post.html')

    def test_post_edit_redirect_anonymous_on_post(self):
        response = self.guest_client.get(
            f'/{self.user_2.username}/{self.post.id}/edit/')
        self.assertRedirects(
            response,
            f'/auth/login/?next=/{self.user_2.username}/{self.post.id}/edit/')
