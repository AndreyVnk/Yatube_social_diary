from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (PasswordChangeForm, PasswordResetForm,
                                       SetPasswordForm, UserCreationForm)

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # укажем модель, с которой связана создаваемая форма
        model = User
        # укажем, какие поля должны быть видны в форме и в каком порядке
        fields = ('first_name', 'last_name', 'username', 'email')


class PasswordChange(PasswordChangeForm):
    # укажем модель, с которой связана создаваемая форма
    model = User
    # укажем, какие поля должны быть видны в форме и в каком порядке
    fields = ('old_password', 'new_password1', 'new_password2')


class PasswordReset(PasswordResetForm):
    # укажем модель, с которой связана создаваемая форма
    model = User
    # укажем, какие поля должны быть видны в форме и в каком порядке
    fields = ('emai')


class SetPassword(SetPasswordForm):
    # укажем модель, с которой связана создаваемая форма
    model = User
    # укажем, какие поля должны быть видны в форме и в каком порядке
    fields = ('new_password1', 'new_password2')
