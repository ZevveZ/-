from django import forms

from scutmocc.models import MyUser


class MyUserRegisterForm(forms.MOdelForm):
    class Meta:
        model = MyUser
        fields = ['email']