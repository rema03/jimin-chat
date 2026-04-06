from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from .models import User


class StyledFieldsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            widget.attrs['class'] = 'app-input'
            widget.attrs.setdefault('placeholder', field.label)

            if field_name in {'password1', 'new_password1'}:
                widget.attrs.setdefault('autocomplete', 'new-password')
            elif field_name in {'password', 'old_password', 'new_password2'}:
                widget.attrs.setdefault('autocomplete', 'current-password')
            elif field_name == 'username':
                widget.attrs.setdefault('autocomplete', 'username')
            elif field_name == 'name':
                widget.attrs.setdefault('autocomplete', 'name')


class CustomAuthenticationForm(StyledFieldsMixin, AuthenticationForm):
    pass


class CustomUserCreationForm(StyledFieldsMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('name', 'age',)


class UserProfileForm(StyledFieldsMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'age']


class CustomPasswordChangeForm(StyledFieldsMixin, PasswordChangeForm):
    pass
