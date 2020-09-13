from django.urls import path

from .bucket_views import *
from .file_views import *

bucket_urlpatterns = [
    path("bucket/get", get_bucket),
    path("bucket/get_all", get_buckets),
    path("bucket/del", del_bucket),
    path("bucket/add", add_bucket),
]

file_urlpatterns = [
    path("file/batchUpload", batch_upload),
    path("file/get", get_file),
    path("file/del", del_file),
]

urlpatterns = bucket_urlpatterns + file_urlpatterns
