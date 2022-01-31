from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Class Create/Edit Post Form."""

    class Meta:
        model = Post
        fields = (
            "text",
            "group",
            "image",
        )


class CommentForm(forms.ModelForm):
    """Class Create Comment Form."""

    class Meta:
        model = Comment
        fields = ("text",)
