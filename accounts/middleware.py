import jwt
from django.conf import settings
from django.contrib.auth import get_user_model, login

User = get_user_model()

class JiminAccountsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            token = request.COOKIES.get('jimin_token')
            if token:
                try:
                    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
                    
                    email = payload.get('email')
                    username = payload.get('username')
                    name = payload.get('name', '')
                    
                    if email and username:
                        user, created = User.objects.get_or_create(
                            email=email,
                            defaults={
                                'username': username,
                                'name': name,
                            }
                        )
                        login(request, user)
                except jwt.PyJWTError:
                    pass
                except Exception:
                    pass

        return self.get_response(request)
