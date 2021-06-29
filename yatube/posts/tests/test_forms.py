from django.test import Client, TestCase
from django.urls import reverse

from ..models import User, Post, Group


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание группы')
        cls.post = Post.objects.create(author=cls.user,
                                       text='Тестовый текст поста',
                                       group=cls.group)

    def test_create_task(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст поста',
                group=self.group.id
            ).exists()
        )
