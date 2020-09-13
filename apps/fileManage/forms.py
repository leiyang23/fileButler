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
