from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """accounts 서비스(SSO)에서 동기화되는 로컬 유저 모델"""
    name = models.CharField(max_length=50, verbose_name="이름", default="")

    def __str__(self):
        return self.username