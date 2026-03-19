from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('name', 'age',)
    # accounts/forms.py 추가

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'age'] # 수정 허용할 필드