from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Class Create/Edit Post."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)


class CommentForm(forms.ModelForm):
    """Class create comment."""

    class Meta:
        model = Comment
        fields = ('text',)
