from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db.models import EmailField, CharField, BooleanField, DecimalField, DateTimeField
from django.contrib.auth.hashers import make_password, identify_hasher


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, name, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError('Укажите email')
        if not name:
            raise ValueError('Укажите имя')
        if not password:
            raise ValueError('Задайте пароль')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.staff = is_staff
        user.admin = is_admin
        user.is_active = is_active
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password=password, is_staff=True, is_admin=True)
        return user

    def create_staff(self, email, name, password=None):
        user = self.create_user(email, name, password=password, is_staff=True, is_admin=False)
        return user


class User(AbstractBaseUser):
    email = EmailField(max_length=255, unique=True)
    name = CharField(max_length=255)
    staff = BooleanField(default=False)
    admin = BooleanField(default=False)
    is_active = BooleanField(default=True)
    timestamp = DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    def get_name(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        if self.admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    def save(self, *args, **kwargs):
        try:
            _alg = identify_hasher(self.password)
        except ValueError:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
