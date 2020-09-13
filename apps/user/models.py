import time
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.db import models


def random_user_id():
    """生成随机ID"""
    return "u" + str(int(time.time()))


def random_user_name():
    """生成随机用户名"""
    return "user" + str(int(time.time()))


class User(models.Model):
    """平台用户"""
    uid = models.CharField(verbose_name="用户ID", default=random_user_id, unique=True, primary_key=True, max_length=11)
    name = models.CharField(verbose_name="用户名", max_length=80, unique=True, default=random_user_name)
    email = models.EmailField(verbose_name="邮箱")
    password = models.CharField(verbose_name="密码", max_length=300, help_text="hash加密")

    is_active = models.IntegerField(verbose_name="是否激活", choices=((0, "禁用"), (1, "可用")), default=1)

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    change_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)

    @property
    def token(self):
        return self._generate_token()

    def _generate_token(self):
        payload = {
            "exp": datetime.now() + timedelta(days=1),
            "iat": datetime.now(),
            "data": {
                "email": self.email,
                "uid": self.uid
            }
        }
        token = jwt.encode(payload, settings.SECRET_KEY)
        return token.decode("utf-8")


class VerifyEmail(models.Model):
    """注册验证码"""
    code = models.IntegerField(verbose_name="六位验证码")
    email = models.EmailField(verbose_name="注册邮箱", unique=True)

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    change_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)
