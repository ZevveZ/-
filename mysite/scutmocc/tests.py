# Create your tests here.
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .import views


class PersonalRegistrationTestCase(TestCase):
    # 手工测试通过：注册时提供所有信息，两次密码一致
    @classmethod
    def setUpTestData(cls):
        pass

    def test_register_with_existing_username(self):
        # 创建用户
        User.objects.create(username='201430550428', password='hello')
        response = self.client.post(reverse(views.personal_registration), {'xuehao': '201430550428',
                                                                'realname': '柯昭武',
                                                                'nickname': 'zev',
                                                                'email': '1062115648',
                                                                'password': 'hello',
                                                                'sec_psd': 'hello'})
        self.assertFormError(response, form='form', field=None, errors='学号已经被注册！')

