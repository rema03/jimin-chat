import urllib.parse
import jwt

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect


User = get_user_model()


class JiminAccountsMiddleware:
    """
    [SSO 자동 로그인 미들웨어]
    사용자가 채팅방에 접속할 때 요청(request)에 담긴 'jimin_token' 쿠키를 확인하여,
    토큰이 유효하면 로컬 채팅 데이터베이스에 사용자가 있는지 확인하고 
    없으면 자동으로 생성(update_or_create)한 뒤 로그인 세션을 맺어줍니다.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            token = request.COOKIES.get('jimin_token')
            if token:
                self._authenticate_from_token(request, token)
        return self.get_response(request)

    @staticmethod
    def _authenticate_from_token(request, token):
        try:
            # 중앙 인증 서비스(accounts)에서 발급한 JWT 해독
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        except jwt.PyJWTError:
            return

        email = payload.get('email')
        username = payload.get('username') or payload.get('sub')
        name = payload.get('name', '')

        if not email or not username:
            return

        # 토큰 정보가 유효하면 채팅(로컬) 유저 객체 조회 및 업데이트(없으면 생성)
        user, created = User.objects.update_or_create(
            email=email,
            defaults={'username': username, 'name': name},
        )
        
        # Django 세션 로그인 처리
        login(request, user)


def signup_view(request):
    """
    [회원가입 리다이렉트 뷰]
    사용자가 '/accounts/signup/' 경로로 접속하면, 
    채팅 앱에서는 회원가입을 직접 처리하지 않고 
    외부에 있는 중앙 계정 서비스(accounts.jimindev.com)의 회원가입 페이지로 튕겨 보냅니다.
    이때 회원가입이 끝나면 다시 현재 서비스로 돌아오도록 callbackUrl을 붙여줍니다.
    """
    callback = request.build_absolute_uri('/')
    return redirect(f"{settings.ACCOUNTS_URL}/signup?callbackUrl={urllib.parse.quote(callback)}")


def login_view(request):
    """
    [로그인 리다이렉트 뷰]
    사용자가 '/accounts/login/' 경로로 접속하면, 
    채팅 앱에서는 아이디/비밀번호를 직접 묻지 않고 
    중앙 계정 서비스(accounts.jimindev.com)의 로그인 페이지로 보냅니다.
    마찬가지로 로그인이 완료되면 되돌아올 callbackUrl을 붙여 보냅니다.
    """
    callback = request.build_absolute_uri('/')
    return redirect(f"{settings.ACCOUNTS_URL}/login?callbackUrl={urllib.parse.quote(callback)}")


def logout_view(request):
    """
    [로그아웃 리다이렉트 뷰]
    사용자가 로그아웃 버튼을 누르면, 
    먼저 현재 채팅 서비스 내의 로그인 세션을 지우고, 
    중앙 계정 서비스로 리다이렉트 시켜 전체 시스템(SSO)에서의 로그아웃을 유도합니다.
    """
    auth_logout(request)
    callback = request.build_absolute_uri('/')
    return redirect(f"{settings.ACCOUNTS_URL}/logout?callbackUrl={urllib.parse.quote(callback)}")
