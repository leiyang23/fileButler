import time
import uuid

from django.db import models


class Bucket(models.Model):
    """空间"""
    bid = models.CharField(verbose_name="空间ID", max_length=11, primary_key=True)
    name = models.CharField(verbose_name="名称", max_length=120, unique=True)
    capacity = models.IntegerField(verbose_name="容量", help_text="单位：字节（bytes)", default=1024 * 1024 * 1024 * 10)
    single_max_size = models.IntegerField(verbose_name="单文件限制大小", default=1024 * 1024 * 200)
    size = models.IntegerField(verbose_name="当前容量", default=0)

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    change_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)

    def __str__(self):
        return f"<{self.name},{self.size}>"

    class Meta:
        verbose_name_plural = verbose_name = "空间"


class File(models.Model):
    """文件"""
    fid = models.UUIDField(verbose_name="文件ID", primary_key=True, default=uuid.uuid4)
    name = models.CharField(verbose_name="文件名", max_length=200)
    hash = models.CharField(verbose_name="hash", max_length=100)
    size = models.IntegerField(verbose_name="大小", help_text="单位：字节")
    prefix = models.CharField(verbose_name="前缀", help_text="路径前缀", max_length=120)

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    change_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)


class BucketAndFile(models.Model):
    """空间和文件：一对多"""
    bid = models.CharField(verbose_name="空间ID", max_length=11)
    fid = models.CharField(verbose_name="文件ID", max_length=36, unique=True)


class UserAndBucket(models.Model):
    """用户和空间：一对多"""
    uid = models.CharField(verbose_name="用户ID", max_length=11)
    bid = models.CharField(verbose_name="空间ID", max_length=11, unique=True)
