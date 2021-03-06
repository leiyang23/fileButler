import time
import uuid

from django.db import models


def random_bucket_id():
    """生成随机ID"""
    return "b" + str(int(time.time()))


class Bucket(models.Model):
    """空间"""
    bid = models.CharField(verbose_name="空间ID", max_length=11, default=random_bucket_id, primary_key=True)
    name = models.CharField(verbose_name="名称", max_length=120, unique=True)
    capacity = models.IntegerField(verbose_name="容量", help_text="单位：字节（bytes)", default=1024 * 1024 * 1024 * 10)
    single_max_size = models.IntegerField(verbose_name="单文件限制大小", default=1024 * 1024 * 200)

    allow_origins = models.CharField(verbose_name="允许访问域名", default="*", max_length=120, help_text="多个域名用逗号分隔")
    max_age = models.IntegerField(verbose_name='缓存时长', default=3600*1, )

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    change_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = verbose_name = "空间"


class File(models.Model):
    """文件"""
    fid = models.CharField(verbose_name="文件ID", primary_key=True, default=uuid.uuid4, max_length=36)
    name = models.CharField(verbose_name="文件名", max_length=200)
    content_type = models.CharField(verbose_name="文件类型", max_length=100)
    size = models.IntegerField(verbose_name="大小", help_text="单位：字节")
    prefix = models.CharField(verbose_name="前缀", help_text="路径前缀", max_length=120)

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    change_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)

    def __str__(self):
        return f"<{self.name},{self.size}>"

    class Meta:
        verbose_name_plural = verbose_name = "文件"


class BucketAndFile(models.Model):
    """空间和文件：一对多"""
    bid = models.CharField(verbose_name="空间ID", max_length=11)
    fid = models.CharField(verbose_name="文件ID", max_length=36, unique=True)


class UserAndBucket(models.Model):
    """用户和空间：一对多"""
    uid = models.CharField(verbose_name="用户ID", max_length=11)
    bid = models.CharField(verbose_name="空间ID", max_length=11, unique=True)
