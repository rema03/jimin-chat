from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from .forms import CustomUserCreationForm, UserProfileForm

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save(); return redirect('chat:friend_list')
    else: form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})

# [추가] 비밀번호 변경 뷰
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('chat:friend_list')