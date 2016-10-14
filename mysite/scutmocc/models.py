from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


# Create your models here.

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser, PermissionsMixin):
    # Account
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_superuser


class Person(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    Nickname = models.CharField(max_length=10, null=False)
    College = models.ForeignKey()
    Sex = models.BooleanField()
    Signature = models.CharField(max_length=100)
    Zc_Date = models.DateField(False, True)
    Fb_sum = models.IntegerField()
    Hf_sum = models.IntegerField()
    Gz_sum = models.IntegerField()
    Bgz_sum = models.IntegerField()
    Sc_sum = models.IntegerField()
    Rank = models.IntegerField()
