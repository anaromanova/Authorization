from django.utils import timezone
import string, secrets
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.crypto import get_random_string

from .utils import get_random_code

class UserManager(BaseUserManager):
    def create_user(self, phone, **extra):
        user = self.model(phone=phone, **extra)
        user.set_unusable_password()
        user.invite_code = self._generate_invite_code()
        user.save()
        return user

    def _generate_invite_code(self):
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(alphabet) for _ in range(6))
            if not User.objects.filter(invite_code=code).exists():
                return code

class User(AbstractBaseUser):
    phone = models.CharField(max_length=15, unique=True)
    invite_code = models.CharField(max_length=6, unique=True, default=get_random_code)
    used_invite = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='referrals'
    )
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'phone'
    objects = UserManager()

    @classmethod
    def _generate_invite_code(cls):
        # генерим случайную строку длиной 8 и проверяем, что её ещё нет в базе
        while True:
            code = get_random_string(length=8)
            if not cls.objects.filter(invite_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self._generate_invite_code()
        super().save(*args, **kwargs)

class SMSCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)
