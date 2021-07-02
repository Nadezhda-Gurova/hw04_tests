from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
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
                text=form_data['text'],
                group=form_data['group']
            ).exists()
        )

    def test_post_edit(self):
        form_data = {
            'text': 'Измененный текст',
        }
        self.authorized_client.post(reverse('post_edit', kwargs={
            'username': self.user.username, 'post_id': self.post.id
        }),
                                    data=form_data
                                    )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, form_data['text'])

    def test_new_post_create_unauthorized_user(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст создает неавторизованный пользователь',
            'group': self.group.id,
        }
        self.guest_client.post(
            reverse('new_post'), data=form_data,
        )
        self.assertEqual(Post.objects.count(), tasks_count)
