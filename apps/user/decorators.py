import jwt
from django.conf import settings
from django.http import JsonResponse

from .models import User


def require_login(view_func):
    def wrapper(req, *args, **kwargs):
        try:
            # 请求头形如 header:{"Authorization":"token eyJ0eXAiOiJKVNiJ9.eyJifX0.RG62WjWO6AtUyTQ"}
            auth = req.META.get('HTTP_AUTHORIZATION').split()
        except AttributeError:
            return JsonResponse({
                "errcode": -1,
                "msg": "未认证的请求",
                "data": {"error": "需要在请求头中添加Authorization参数"}
            })

        if auth[0].lower() != "token":
            return JsonResponse({
                "errcode": -1,
                "msg": "未认证的请求",
                "data": {"error": "Authorization参数格式需要以token 开头"}
            })

        try:
            auth_params = jwt.decode(auth[1], settings.SECRET_KEY, algorithms=['HS256'])
            email = auth_params.get('data').get('email')
            req.email = email

        except jwt.ExpiredSignatureError:
            return JsonResponse({
                "errcode": -1,
                "msg": "认证已过期"
            })

        except jwt.InvalidTokenError:
            return JsonResponse({
                "errcode": -1,
                "msg": "非法的认证token"
            })

        except Exception as e:
            return JsonResponse({
                "errcode": -1,
                "msg": "未知的错误：" + str(e)
            })

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({
                "errcode": -1,
                "msg": "未注册的用户"
            })

        if not user.is_active:
            return JsonResponse({
                "errcode": -1,
                "msg": "该用户未激活"
            })

        return view_func(req, *args, **kwargs)

    return wrapper
