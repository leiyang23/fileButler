import re
from string import ascii_letters, digits
from datetime import datetime, timedelta

from django import forms
from django.contrib.auth.hashers import make_password

from .models import RegisterCode, User


def check_email_existed(email):
    try:
        user = User.objects.get(email=email)
        if user:
            raise forms.ValidationError("邮箱已被注册")
    except User.DoesNotExist:
        pass


class RegisterEmailForm(forms.Form):
    """验证注册邮箱"""
    email = forms.EmailField(required=True, validators=[check_email_existed])

    def clean(self):
        try:
            email = self.cleaned_data['email']

            obj = RegisterCode.objects.get(email=email)
            if datetime.now() - obj.change_time < timedelta(minutes=1):
                raise forms.ValidationError("请求太频繁，请稍后再试")

        except KeyError:
            pass

        except RegisterCode.DoesNotExist:
            pass

        return self.cleaned_data


def check_user_name(name):
    # todo: 对名称字符进行验证
    try:
        user = User.objects.get(name=name)
        raise forms.ValidationError("用户名已存在")

    except User.DoesNotExist:
        pass


def check_password(password):
    """用户原始密码校验
    字母、数字、@#$&*-_
    """
    if not re.compile("^[0-9a-zA-Z@#$&\*\-_]{8,17}$").match(password):
        raise forms.ValidationError("密码不符合格式")


def check_code(code):
    if not re.compile("^[123456789]{6}$").match(code):
        raise forms.ValidationError("邮箱验证码不符合格式")


class RegisterForm(forms.Form):
    """注册参数验证"""
    name = forms.CharField(required=True, min_length=1, max_length=80, validators=[check_user_name])
    email = forms.EmailField(required=True, )
    password = forms.CharField(required=True, validators=[check_password])

    code = forms.CharField(required=True, validators=[check_code])

    def clean(self):
        try:
            email = self.cleaned_data['email']
            code = self.cleaned_data['code']
            password = self.cleaned_data['password']

            obj = RegisterCode.objects.get(email=email)
            if datetime.now() - obj.change_time > timedelta(minutes=15):
                raise forms.ValidationError("验证码已过期")

            if str(code) != str(obj.code):
                raise forms.ValidationError("验证码不正确")

            password = make_password(password)
            self.cleaned_data["password"] = password
            return self.cleaned_data

        except KeyError:
            pass
        except RegisterCode.DoesNotExist:
            raise forms.ValidationError("请核对该邮箱是否发送验证码")
