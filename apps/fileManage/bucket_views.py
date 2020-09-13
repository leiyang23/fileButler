from django.db.models import Sum
from django.db.transaction import atomic
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from user.decorators import require_login
from user.models import User
from .forms import BucketForm
from .models import Bucket, UserAndBucket, File, BucketAndFile


@require_login
@require_GET
def get_buckets(req):
    email = req.email

    user = User.objects.get(email=email)

    bids = UserAndBucket.objects.filter(uid=user.uid).values_list("bid")
    buckets = Bucket.objects.filter(bid__in=bids).values("name", "create_time")

    return JsonResponse({
        "errcode": 0,
        "msg": "已获取所有bucket",
        "data": list(buckets)
    })


@require_login
@require_GET
def get_bucket(req):
    name = req.GET.get("name", None)
    email = req.email

    try:
        user = User.objects.get(email=email)
        bucket = Bucket.objects.get(name=name)

        UserAndBucket.objects.get(bid=bucket.pk, uid=user.pk)

        files_id = BucketAndFile.objects.filter(bid=bucket.bid).values_list("fid")
        files_id = [qz[0] for qz in files_id]
        total_size = File.objects.filter(fid__in=files_id).aggregate(total_size=Sum("size"))['total_size']

        return JsonResponse({
            "errcode": 0,
            "msg": "已获取bucket信息",
            "data": {
                "name": bucket.name,
                "bid": bucket.bid,
                "capacity": bucket.capacity,
                "size": total_size,
                "create_time": bucket.create_time,
                "change_time": bucket.change_time,
            }
        })

    except UserAndBucket.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "该bucket不属于你"
        })
    except Bucket.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "bucket不存在"
        })


@require_login
@require_POST
def del_bucket(req):
    name = req.POST.get("name", None)
    email = req.email
    try:
        user = User.objects.get(email=email)
        bucket = Bucket.objects.get(name=name)

        user_and_bucket = UserAndBucket.objects.get(bid=bucket.pk, uid=user.pk)

        with atomic():
            bucket.delete()
            user_and_bucket.delete()

        return JsonResponse({
            "errcode": 0,
            "msg": "已删除该bucket",
        })

    except UserAndBucket.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "该bucket不属于你"
        })
    except Bucket.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "bucket不存在"
        })


@require_login
@require_POST
def add_bucket(req):
    form = BucketForm(req.POST)
    if form.is_valid():
        name = form.cleaned_data['name']
        try:
            with atomic():
                bucket = Bucket.objects.create(name=name)
                user = User.objects.get(email=req.email)
                UserAndBucket.objects.create(bid=bucket.bid, uid=user.uid)

            return JsonResponse({
                "errcode": 0,
                "msg": "添加bucket成功"
            })
        except Exception as e:
            return JsonResponse({
                "errcode": -1,
                "msg": "添加bucket出现错误：" + str(e)
            })

    else:
        return JsonResponse({
            "errcode": -1,
            "msg": form.errors
        })


@require_login
@require_GET
def get_files(req):
    uid = req.uid
    bucket_name = req.GET.get("bucket", None)

    try:
        bucket = Bucket.objects.get(name=bucket_name)
        UserAndBucket.objects.get(uid=uid, bid=bucket.bid)

        bucket_and_files = BucketAndFile.objects.filter(bid=bucket.bid).values_list("fid")
        fids = [i[0] for i in bucket_and_files]
        files = File.objects.filter(fid__in=fids).values()

        return JsonResponse({
            "errcode": 0,
            "msg": "成功获取",
            "data": list(files)
        })

    except UserAndBucket.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "该bucket不属于你"
        })
    except Bucket.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "该bucket不存在"
        })
