from django.contrib.auth.views import (PasswordChangeView,
                                       PasswordResetConfirmView,
                                       PasswordResetView)
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm, PasswordChange, PasswordReset, SetPassword


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class CustomPasswordChange(PasswordChangeView):
    form_class = PasswordChange
    success_url = reverse_lazy('users/password_change/done')
    template_name = 'users/password_change_form.html'


class CustomPasswordReset(PasswordResetView):
    form_class = PasswordReset
    success_url = reverse_lazy('users/password_reset/done')
    template_name = 'users/password_reset_form.html'


class CustomPasswordConfirm(PasswordResetConfirmView):
    form_class = SetPassword
    success_url = reverse_lazy('users/password_reset_complete')
    template_name = 'users/password_reset_complete.html'
