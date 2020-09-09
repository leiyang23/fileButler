import random
import time
from string import ascii_letters, digits
from typing import Callable

from django.db import models


def random_id(prefix: str) -> Callable:
    """生成随机ID"""

    def inner():
        return prefix + str(int(time.time()))

    return inner


def gen_key(length: int) -> Callable:
    """生成随机Key"""

    def inner():
        return "".join(random.choices(ascii_letters + digits, k=length))

    return inner


class User(models.Model):
    """平台用户"""
    uid = models.CharField(verbose_name="用户ID", default=random_id("u"), unique=True, primary_key=True, max_length=11)
    name = models.CharField(verbose_name="用户名", max_length=80)
    email = models.EmailField(verbose_name="邮箱")
    password = models.CharField(verbose_name="密码", max_length=300, help_text="hash加密")

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    change_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)


class Group(models.Model):
    """用户群组"""
    gid = models.CharField(verbose_name="群组ID", default=random_id("g"), unique=True, primary_key=True, max_length=11)
    name = models.CharField(verbose_name="群组名", max_length=80)

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    change_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)


class AccessPolicy(models.Model):
    """访问策略"""
    aid = models.CharField(verbose_name="策略ID", default=random_id("a"), unique=True, primary_key=True, max_length=11)
    name = models.CharField(verbose_name="名称", max_length=80)
    access_key = models.CharField(verbose_name="AccessKey", default=gen_key(40), unique=True, max_length=40)
    secret_key = models.CharField(verbose_name="SecretKey", default=gen_key(40), unique=True, max_length=40)

    status = models.IntegerField(verbose_name="状态", choices=((0, "停用"), (1, "启用")))

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    change_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)


class UserAndGroup(models.Model):
    """用户和群组：多对多"""
    uid = models.CharField(verbose_name="用户ID", max_length=11)
    gid = models.CharField(verbose_name="群组ID", max_length=11)


class UserAndAccessPolicy(models.Model):
    """用户和策略：一对多"""
    uid = models.CharField(verbose_name="用户ID", max_length=11)
    aid = models.CharField(verbose_name="策略ID", max_length=11, unique=True)


class GroupAndAccessPolicy(models.Model):
    """群组和策略：一对多"""
    gid = models.CharField(verbose_name="群组ID", max_length=11)
    aid = models.CharField(verbose_name="策略ID", max_length=11, unique=True)
