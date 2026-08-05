from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def home_view(request):
    """메인 페이지: 로그인 여부에 따라 리다이렉트"""
    if request.user.is_authenticated:
        return redirect('chat:friend_list')
    return redirect('login')


from chat import accounts as chat_accounts

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', chat_accounts.login_view, name='login'),
    path('accounts/signup/', chat_accounts.signup_view, name='signup'),
    path('accounts/logout/', chat_accounts.logout_view, name='logout'),
    path('chat/', include('chat.urls')),
    path('', home_view, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)