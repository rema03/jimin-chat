from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# 메인 페이지 접속 시 로그인 여부에 따라 보내주는 곳을 결정하는 함수
def home_view(request):
    if request.user.is_authenticated:
        return redirect('chat:friend_list')  # 로그인 되어 있으면 친구 목록으로
    return redirect('login')  # 로그인 안 되어 있으면 로그인 창으로

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chat.urls')),
    
    # 메인 주소('') 접속 시 처리
    path('', home_view, name='home'), 
]

# 미디어 파일 서빙 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)