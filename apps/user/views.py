import random

from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import RegisterEmailForm, RegisterForm
from .models import RegisterCode, User


@require_POST
def get_register_code(req):
    form = RegisterEmailForm(req.POST)

    if form.is_valid():
        email = form.cleaned_data['email']
        code = "".join(random.choices("123456789", k=6))

        RegisterCode.objects.update_or_create(email=email, defaults={"code": code})

        recipients = [email]
        if send_mail("注册验证码", code, settings.EMAIL_HOST_USER, recipients):
            return JsonResponse({
                "errcode": 0,
                "msg": "success",
                "data": {"code": code}
            })
        else:
            return JsonResponse({
                "errcode": -1,
                "msg": "email send fail, please try again"
            })
    else:
        return JsonResponse({
            "errcode": -1,
            "msg": "error params",
            "data": {"error": form.errors}
        })


@require_POST
def register(req):
    form = RegisterForm(req.POST)
    if form.is_valid():
        name = form.cleaned_data['name']
        email = form.cleaned_data["email"]
        password = form.cleaned_data['password']

        User.objects.create(name=name, email=email, password=password)

        return JsonResponse({
            "errcode": 0,
            "msg": "success",
        })
    else:
        return JsonResponse({
            "errcode": -1,
            "msg": "register error",
            "data": {"error": form.errors}
        })


def login(req):
    pass


def logout(req):
    pass


def retrieve(req):
    pass
