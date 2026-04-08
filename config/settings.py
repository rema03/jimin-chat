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


APP_NAME = os.getenv('APP_NAME', 'Jimin Chat')
APP_TAGLINE = os.getenv('APP_TAGLINE', '친구들과 실시간으로 대화하세요')
APP_VERSION = os.getenv('APP_VERSION', '1.2')

# 2. 보안 설정 (배포 시 관리 필요)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-local-dev-key')
DEBUG = env_to_bool('DJANGO_DEBUG', default=True)
ALLOWED_HOSTS = env_to_list('DJANGO_ALLOWED_HOSTS', default='127.0.0.1,localhost')
if DEBUG:
    ALLOWED_HOSTS = sorted(set(ALLOWED_HOSTS) | set(get_local_dev_hosts()))

# 3. 애플리케이션 정의
INSTALLED_APPS = [
    'daphne', # Channels를 위해 반드시 맨 위에 위치
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

# 서버 설정 (ASGI/Channels)
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Channels 레이어 설정 (로컬 테스트용 메모리 레이어)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# 5. 데이터베이스 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 6. 비밀번호 검증 및 인증
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'accounts.User'
LOGIN_REDIRECT_URL = 'chat:friend_list'
LOGOUT_REDIRECT_URL = 'login'

# 7. 지역 및 언어 설정
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# 8. 정적 파일 및 미디어 파일 설정 (중요!)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 이미지 업로드를 위한 설정
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
