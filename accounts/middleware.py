import jwt
from django.conf import settings
from django.contrib.auth import get_user_model, login

User = get_user_model()


class JiminAccountsMiddleware:
    """JWT(jimin_token) 쿠키 기반 SSO 자동 로그인 미들웨어"""

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
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        except jwt.PyJWTError:
            return

        email = payload.get('email')
        username = payload.get('username') or payload.get('sub')
        name = payload.get('name', '')

        if not email or not username:
            return

        user, created = User.objects.update_or_create(
            email=email,
            defaults={'username': username, 'name': name},
        )
        login(request, user)
