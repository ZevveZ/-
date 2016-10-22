# coding: utf-8
from django import forms


class ActivityForm(forms.Form):
    name = forms.CharField(label='社团名称', max_length=20)
    account = forms.EmailField(label='绑定邮箱')
    introduce = forms.CharField(label='社团简介', widget=forms.Textarea, max_length=200)
    password = forms.CharField(label='账号密码', widget=forms.PasswordInput, max_length=20)
    second_psd = forms.CharField(widget=forms.PasswordInput, max_length=20)

    def clean(self):
        cleaned_data = super(ActivityForm, self).clean()
        psd = cleaned_data.get('password')
        sec_psd = cleaned_data.get('second_psd')

        if psd != sec_psd:
            raise forms.ValidationError("两次密码输入不一致!", code='psd-inequality')


class PersonalForm(forms.Form):
    xuehao = forms.CharField(max_length=15)
    realname = forms.CharField(max_length=30)
    nickname = forms.CharField(max_length=10)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    sec_psd = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(PersonalForm, self).clean()
        psd = cleaned_data.get('password')
        sec_psd = cleaned_data.get('sec_psd')

        if psd != sec_psd:
            raise forms.ValidationError("两次密码输入不一致!", code='psd-inequality')



