import random

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import VerifyEmailForm, RegisterForm, LoginForm, RetrieveForm
from .models import VerifyEmail, User


@require_POST
def get_email_code(req):
    """获取邮箱验证码"""
    form = VerifyEmailForm(req.POST)

    if form.is_valid():
        email = form.cleaned_data['email']
        code = "".join(random.choices("123456789", k=6))

        VerifyEmail.objects.update_or_create(email=email, defaults={"code": code})

        recipients = [email]
        if send_mail("注册验证码", code, settings.EMAIL_HOST_USER, recipients):
            return JsonResponse({
                "errcode": 0,
                "msg": "发送验证码成功",
                "data": {"code": code}
            })
        else:
            return JsonResponse({
                "errcode": -1,
                "msg": "验证码未发送，请重试"
            })
    else:
        return JsonResponse({
            "errcode": -1,
            "msg": "错误的邮箱格式",
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
            "msg": "注册成功",
        })
    else:
        return JsonResponse({
            "errcode": -1,
            "msg": "注册失败",
            "data": {"error": form.errors}
        })


@require_POST
def login(req):
    form = LoginForm(req.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        try:
            user = User.objects.get(email=email)

            if check_password(password, user.password):
                return JsonResponse({
                    "errcode": 0,
                    "msg": "登录成功",
                    "data": {"token": user.token}
                })
            else:
                return JsonResponse({
                    "errcode": -1,
                    "msg": "用户名或密码错误"
                })
        except User.DoesNotExist:
            return JsonResponse({
                "errcode": -1,
                "msg": "该邮箱还未注册"
            })
    else:
        return JsonResponse({
            "errcode": -1,
            "msg": "登录参数错误",
            "data": {"error": form.errors}
        })


def logout(req):
    pass


@require_POST
def retrieve(req):
    form = RetrieveForm(req.POST)
    if form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data['password']

        user = User.objects.get(email=email)
        user.password = password
        user.save()

        return JsonResponse({
            "errcode": 0,
            "msg": "登录密码更新成功",
        })
    else:
        return JsonResponse({
            "errcode": -1,
            "msg": "密码找回失败",
            "data": {"error": form.errors}
        })
