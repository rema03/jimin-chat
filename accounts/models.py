from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    name = models.CharField(max_length=50, verbose_name="이름")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="나이")

    def __str__(self):
        return self.username