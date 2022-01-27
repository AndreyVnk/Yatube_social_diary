from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Subquery

from .forms import CommentForm, PostForm
from .models import Group, Post, User, Follow
from .utils import paginator


def index(request):
    """Start page."""

    page_obj = paginator(request, Post.objects.all())

    context = {
        'title': 'Последние обновления на сайте',
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Group list page."""

    group = get_object_or_404(Group, slug=slug)
    page_obj = paginator(request, group.posts.all())

    context = {
        'group': group,
        'page_obj': page_obj,
        'title': f'Записи сообщества {group.title}'

    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Profile page."""

    author = get_object_or_404(
        User, username=username
    )
    page_obj = paginator(request, Post.objects.filter(
        author__username=username)
    )
    if not request.user.is_authenticated:
        return render(request, 'posts/profile.html', {
            'author': author,
            'page_obj': page_obj,
        })
    following = True
    authors = Follow.objects.filter(
        user=request.user
    ).values_list('author_id', flat=True)
    if author.id not in authors:
        following = False
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Post detail page."""

    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()

    context = {
        'form': CommentForm(),
        'post': post,
        'comments': comments

    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Creating post page."""

    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author.username)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Editing post page."""

    post_ed = get_object_or_404(Post, pk=post_id)

    if post_ed.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_ed
    )

    if form.is_valid():
        post_ed.save()
        return redirect(
            'posts:post_detail', post_id=post_id
        )

    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):

    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):

    authors = Follow.objects.filter(user=request.user)
    posts_list = Post.objects.filter(
        author_id__in=Subquery(authors.values('author_id'))
    )
    page_obj = paginator(request, posts_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Subscribe to author."""

    author = get_object_or_404(User, username=username)
    authors = Follow.objects.filter(
        user=request.user
    ).values_list('author_id', flat=True)
    if ((request.user.username != author.username)
            and (author.id not in authors)):

        sub = Follow(
            author=author,
            user=request.user
        )
        sub.save()

    context = {
        'author': author,
        'following': True
    }
    return render(request, 'posts/profile.html', context)


@login_required
def profile_unfollow(request, username):
    """Unsubscribe to author."""

    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        author=author,
        user=request.user
    ).delete()
    context = {
        'author': author,
        'following': False
    }
    return render(request, 'posts/profile.html', context)
