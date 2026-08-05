import urllib.parse

from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect


def signup_view(request):
    """accounts 서비스 회원가입 페이지로 리다이렉트"""
    callback = request.build_absolute_uri('/')
    return redirect(f"{settings.ACCOUNTS_URL}/signup?callbackUrl={urllib.parse.quote(callback)}")


def login_view(request):
    """accounts 서비스 로그인 페이지로 리다이렉트"""
    callback = request.build_absolute_uri('/')
    return redirect(f"{settings.ACCOUNTS_URL}/login?callbackUrl={urllib.parse.quote(callback)}")


def logout_view(request):
    """로컬 세션 삭제 후 accounts 서비스 로그아웃으로 리다이렉트"""
    auth_logout(request)
    callback = request.build_absolute_uri('/')
    return redirect(f"{settings.ACCOUNTS_URL}/logout?callbackUrl={urllib.parse.quote(callback)}")
