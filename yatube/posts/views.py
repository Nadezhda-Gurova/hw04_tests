from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'misc/index.html', {'page': page, })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/group.html', {
        'group': group, 'page': page,
    })


def profile(request, username):
    user = get_object_or_404(User, username=username)
    number_of_posts = Post.objects.filter(author_id=user.id).count()
    paginator = Paginator(user.posts.all(), settings.NUMBER_OF_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'misc/profile.html', {
        'number_of_posts': number_of_posts, 'page': page, 'author': user,
    })


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    number_of_posts = Post.objects.filter(author_id=user.id).count()
    post = get_object_or_404(Post, id=post_id, author_id=user.id)
    return render(request, 'posts/post.html', {
        'number_of_posts': number_of_posts, 'post': post, 'author': user,
    })


@login_required
def new_post(request):
    form = PostForm()
    if request.method == 'GET':
        return render(request, 'posts/new.html', {'form': form, })
    elif request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post: Post = form.save(False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'posts/new.html', {'form': form})
    return render(request, 'posts/new.html', {'form': form, })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.user != post.author:
        return redirect('posts', username=username, post_id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post.save()
        return redirect('posts', username=username, post_id=post_id)
    return render(request, 'posts/new.html', {'form': form, 'post': post})
