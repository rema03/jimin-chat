from django.conf import settings


def app_meta(request):
    return {
        'app_name': settings.APP_NAME,
        'app_tagline': settings.APP_TAGLINE,
        'app_version': settings.APP_VERSION,
    }
