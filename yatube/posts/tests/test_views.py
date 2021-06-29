from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import User, Post, Group


class TaskPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание группы')
        self.post = Post.objects.create(author=self.user,
                                        text='Тестовый текст поста',
                                        group=self.group)
        self.group_2 = Group.objects.create(
            title='Тестовый заголовок 2',
            slug='test-slug-2',
            description='Тестовое описание группы 2')
        self.post_2 = Post.objects.create(author=self.user,
                                          text='Тестовый текст поста 2',
                                          group=self.group_2)

    def test_pages_use_correct_template(self):
        """Функция проверяет шаблон при обращении к view-классам."""
        templates_pages_names = {
            'misc/index.html': reverse('index'),
            'posts/group.html': (
                reverse('group', kwargs={'slug': 'test-slug'})
            ),
            'posts/new.html': reverse('new_post'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_shows_correct_context(self):
        """Функция проверяет словарь контекста главной страницы."""
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page'][0]
        post_id = first_object.id
        post_text = first_object.text
        post_author = first_object.author
        post_group = first_object.group
        self.assertEqual(post_id, self.post_2.id)
        self.assertEqual(post_text, self.post_2.text)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_group, self.group_2)

    def test_group_page_shows_correct_context(self):
        """Функция проверяет словарь контекста страницы группы."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-slug'}))
        test_group = response.context['group']
        test_post = response.context['page'][0]
        self.assertEqual(test_group.title, self.group.title)
        self.assertEqual(test_post.text, self.post.text)

    def test_post_page_shows_correct_context(self):
        """Функция проверяет словарь контекста страницы поста."""
        response = self.authorized_client.get(reverse('posts', kwargs={
            'username': self.user.username, 'post_id': self.post.id}))
        profile = {'username': self.post.author.username,
                   'number_of_posts': self.user.posts.count(),
                   'posts': self.post}
        for value, expect in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expect)

    def test_new_post_page_shows_correct_context(self):
        """Функция проверяет форму страницы создания поста."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_shows_correct_context(self):
        """Функция проверяет форму страницы редактирования поста."""
        response = self.authorized_client.get(reverse('post_edit', kwargs={
            'username': self.user.username,
            'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_page_shows_correct_context(self):
        """Функция проверяет форму страницы пользователя."""
        response = self.authorized_client.get(reverse('profile', kwargs={
            'username': self.user.username}))
        profile = {'user_profile': self.user,
                   'number_of_posts': self.user.posts.count(),
                   'latest_post_id': response.context['page'][0].id,
                   }
        for value, expect in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expect)

    def test_post_on_page_index(self):
        """Функция проверяет, что при создании поста, он появляется на главной
        странице."""
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page'][0]
        post_text = first_object.text
        post_author = first_object.author
        post_group = first_object.group
        self.assertEqual(post_text, self.post_2.text)
        self.assertEqual(post_author, self.post_2.author)
        self.assertEqual(post_group, self.post_2.group)

    def test_post_on_page_group(self):
        """Функция проверяет, что при создании поста,
        он появляется странице группы."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-slug'}))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)

    def test_post_on_other_page(self):
        """Функция проверяет, что созданный пост не попал в группу,
        для которой не был предназначен"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-slug-2'}))
        first_object = response.context['page'][0]
        self.assertNotEqual(first_object, self.post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        for i in range(13):
            cls.post = Post.objects.create(
                text=f'Тестовый пост номер - {i}',
                author=cls.user,
                group=cls.group,

            )

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(reverse('index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context.get('page')), 10)

    def test_index_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page')), 3)

    def test_group_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse('group', kwargs={'slug': 'test-slug'}))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context.get('page')), 10)

    def test_group_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(
            reverse('group', kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context.get('page')), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.client.get(reverse('profile', kwargs={
            'username': self.user.username}))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context.get('page')), 10)

    def test_profile_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('profile', kwargs={
            'username': self.user.username}) + '?page=2')
        self.assertEqual(len(response.context.get('page')), 3)
