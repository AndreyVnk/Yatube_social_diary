from django.contrib.auth.decorators import login_required
from django.db.models import Subquery
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginator


def index(request):
    """Start page."""

    page_obj = paginator(request, Post.objects.select_related("group").all())

    context = {
        "title": "Последние обновления на сайте",
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    """Group list page."""

    group = get_object_or_404(Group, slug=slug)
    page_obj = paginator(request, group.posts.all())

    context = {
        "group": group,
        "page_obj": page_obj,
        "title": f"Записи сообщества {group.title}",
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    """Profile page."""

    author = get_object_or_404(User, username=username)
    page_obj = paginator(
        request, Post.objects.filter(author__username=username)
    )
    following = True

    if request.user.is_authenticated:
        author_in: bool = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
        if not author_in:
            following = False

    context = {"author": author, "page_obj": page_obj, "following": following}
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    """Post detail page."""

    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()

    context = {"form": CommentForm(), "post": post, "comments": comments}
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    """Creating post page."""

    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=post.author.username)

    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, post_id):
    """Editing post page."""

    post_ed = get_object_or_404(Post, pk=post_id)

    if post_ed.author != request.user:
        return redirect("posts:post_detail", post_id=post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post_ed
    )

    if form.is_valid():
        post_ed.save()
        return redirect("posts:post_detail", post_id=post_id)

    context = {"form": form, "is_edit": True}
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    """Add a comment."""

    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    """Show page with following authors."""

    authors = Follow.objects.filter(user=request.user)
    posts_list = Post.objects.filter(
        author_id__in=Subquery(authors.values("author_id"))
    )
    page_obj = paginator(request, posts_list)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    """Subscribe to author."""

    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect("posts:profile", username=username)
    Follow.objects.get_or_create(author=author, user=request.user)

    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    """Unsubscribe to author."""

    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()

    return redirect("posts:profile", username=username)
