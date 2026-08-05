import os
import socket
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def env_to_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_to_list(name, default=''):
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(',') if item.strip()]


def get_local_dev_hosts():
    hosts = {'127.0.0.1', 'localhost', '::1', 'testserver'}
    try:
        hostname = socket.gethostname()
        hosts.add(hostname)
        hosts.update(socket.gethostbyname_ex(hostname)[2])
        for family, _, _, _, sockaddr in socket.getaddrinfo(hostname, None):
            if family in {socket.AF_INET, socket.AF_INET6} and sockaddr:
                hosts.add(sockaddr[0])
    except OSError:
        pass
    return sorted(hosts)


# ── 앱 메타 ──
APP_NAME = os.getenv('APP_NAME', 'Jimin Chat')
APP_TAGLINE = os.getenv('APP_TAGLINE', '친구들과 실시간으로 대화하세요')
APP_VERSION = os.getenv('APP_VERSION', '2.0')

# ── SSO (accounts 서비스 연동) ──
ACCOUNTS_URL = os.getenv('ACCOUNTS_URL', 'http://accounts.localhost')
JWT_SECRET = os.getenv('JWT_SECRET', 'dev-jwt-secret-change-in-production')

# ── 보안 ──
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-local-dev-key')
DEBUG = env_to_bool('DJANGO_DEBUG', default=True)
ALLOWED_HOSTS = env_to_list('DJANGO_ALLOWED_HOSTS', default='127.0.0.1,localhost')
if DEBUG:
    ALLOWED_HOSTS = sorted(set(ALLOWED_HOSTS) | set(get_local_dev_hosts()))
CSRF_TRUSTED_ORIGINS = env_to_list('DJANGO_CSRF_TRUSTED_ORIGINS', default='')
USE_X_FORWARDED_HOST = env_to_bool('DJANGO_USE_X_FORWARDED_HOST', default=True)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = env_to_bool('DJANGO_SESSION_COOKIE_SECURE', default=not DEBUG)
CSRF_COOKIE_SECURE = env_to_bool('DJANGO_CSRF_COOKIE_SECURE', default=not DEBUG)

# ── 앱 ──
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'chat',
    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'accounts.middleware.JiminAccountsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.app_meta',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.getenv('DJANGO_SQLITE_PATH', str(BASE_DIR / 'db.sqlite3')),
    }
}

# 비밀번호 검증은 accounts 서비스에서 처리하므로 로컬에서는 불필요
AUTH_PASSWORD_VALIDATORS = []

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'chat:friend_list'

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

STATIC_URL = os.getenv('DJANGO_STATIC_URL', '/static/')
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = os.getenv('DJANGO_STATIC_ROOT', str(BASE_DIR / 'staticfiles'))

MEDIA_URL = os.getenv('DJANGO_MEDIA_URL', '/media/')
MEDIA_ROOT = os.getenv('DJANGO_MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
