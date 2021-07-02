from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post, User


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
        self.homepage = '/'
        self.group_page = '/group/test-slug/'
        self.new_page = '/new/'
        self.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        self.post = Post.objects.create(author=self.user,
                                        text='Тестовый текст поста',
                                        group=self.group)

    def test_status_code_for_authorized_client(self):
        pages = {
            self.homepage: HTTPStatus.OK,
            self.group_page: HTTPStatus.OK,
            self.new_page: HTTPStatus.OK,
            f'/{self.user.username}/': HTTPStatus.OK,
            f'/{self.user.username}/{self.post.id}/': HTTPStatus.OK,
            f'/{self.user.username}/{self.post.id}/edit/':
                HTTPStatus.FOUND,
            }
        for url_address, response_code in pages.items():
            with self.subTest(address=url_address):
                response = self.authorized_client.get(url_address)
                self.assertEqual(response.status_code, response_code)

    def test_status_code_for_guest_client(self):
        pages = {
            self.homepage: HTTPStatus.OK,
            self.group_page: HTTPStatus.OK,
            self.new_page: HTTPStatus.FOUND,
            f'/{self.user.username}/': HTTPStatus.OK,
            f'/{self.user.username}/{self.post.id}/': HTTPStatus.OK,
            f'/{self.user.username}/{self.post.id}/edit/':
                HTTPStatus.FOUND,
            f'/{self.user_2.username}/{self.post.id}/edit/':
                HTTPStatus.FOUND,
        }
        for url_address, response_code in pages.items():
            with self.subTest(address=url_address):
                response = self.guest_client.get(url_address)
                self.assertEqual(response.status_code, response_code)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'misc/index.html': self.homepage,
            'posts/group.html': self.group_page,
            'posts/new.html': self.new_page,
            'posts/post.html': f'/{self.user.username}/{self.post.id}/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(adress=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_edit_redirect_anonymous_on_post(self):
        response = self.guest_client.get(
            f'/{self.user_2.username}/{self.post.id}/edit/')
        self.assertRedirects(
            response,
            f'/auth/login/?next=/{self.user_2.username}/{self.post.id}/edit/')
