import jwt
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager as DjangoUserManager
from django.db import models
from djchoices import DjangoChoices, ChoiceItem

from main.models.base import BaseModel


class UserManager(DjangoUserManager):
    def create_user(self, email, password=None, **kwargs):
        user = self.model(email=email)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.model(email=email, is_superuser=True)
        user.set_password(password)
        user.save()
        return user


class Role(DjangoChoices):
    admin = ChoiceItem()
    user = ChoiceItem()


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    email = models.EmailField(unique=True)
    role = models.CharField(choices=Role.choices, default=Role.user, max_length=50)

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def token(self):
        """
        Позволяет получить токен пользователя путем вызова user.token, вместо
        user._generate_jwt_token(). Декоратор @property выше делает это
        возможным. token называется "динамическим свойством".
        """
        t = self._generate_jwt_token()
        if type(t) == 'bytes':
            t: bytes
            return t.decode('utf-8')
        return t

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
