from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from .forms import CustomPasswordChangeForm, CustomUserCreationForm, UserProfileForm

import urllib.parse
from django.conf import settings
from django.contrib.auth import logout as auth_logout

def signup_view(request):
    callback_url = request.build_absolute_uri('/')
    redirect_url = f"{settings.ACCOUNTS_URL}/signup?callbackUrl={urllib.parse.quote(callback_url)}"
    return redirect(redirect_url)

def login_view(request):
    callback_url = request.build_absolute_uri('/')
    redirect_url = f"{settings.ACCOUNTS_URL}/login?callbackUrl={urllib.parse.quote(callback_url)}"
    return redirect(redirect_url)

def logout_view(request):
    auth_logout(request)
    callback_url = request.build_absolute_uri('/')
    redirect_url = f"{settings.ACCOUNTS_URL}/logout?callbackUrl={urllib.parse.quote(callback_url)}"
    return redirect(redirect_url)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('chat:friend_list')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('chat:friend_list')
