from django import forms

from .models import Bucket


def check_name_existed(name):
    try:
        Bucket.objects.get(name=name)
        raise forms.ValidationError("空间名已存在")
    except Bucket.DoesNotExist:
        pass


class BucketForm(forms.Form):
    name = forms.CharField(required=True, validators=[check_name_existed])


class BatchUploadForm(forms.Form):
    bucket = forms.CharField(required=True, max_length=80)
    prefix = forms.CharField(required=True, max_length=80)
    file = forms.FileField
