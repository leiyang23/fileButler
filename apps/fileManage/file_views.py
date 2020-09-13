from django.conf import settings
from django.db.models import Sum
from django.db.transaction import atomic
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST, require_GET

from user.decorators import require_login
from .models import Bucket, UserAndBucket, File, BucketAndFile


@require_login
@require_POST
def batch_upload(req):
    uid = req.uid
    bucket_name = req.POST.get("bucket", None)
    prefix = req.POST.get("prefix", None)

    try:
        bucket = Bucket.objects.get(name=bucket_name)
        UserAndBucket.objects.get(uid=uid, bid=bucket.bid)

    except Bucket.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "该bucket不存在"
        })
    except UserAndBucket.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "该bucket不属于你"
        })

    files = req.FILES.getlist("files")

    if len(files) > 10:
        return JsonResponse({
            "errcode": -1,
            "msg": "单次最多上传10个文件"
        })

    files_size = [f.size for f in files]
    if max(files_size) > bucket.single_max_size:
        return JsonResponse({
            "errcode": -1,
            "msg": "该bucket单个文件最大为：" + str(bucket.single_max_size)
        })

    files_id = BucketAndFile.objects.filter(bid=bucket.bid).values_list("fid")
    files_id = [qz[0].replace("-", "") for qz in files_id]
    total_size = File.objects.filter(fid__in=files_id).aggregate(total_size=Sum("size"))['total_size'] or 0

    if sum(files_size) + total_size > bucket.capacity:
        return JsonResponse({
            "errcode": -1,
            "msg": "该bucket已超过最大容量"
        })

    file_objs = []
    for f in files:
        f_path = settings.BASE_DIR.joinpath("media/buckets", bucket_name, prefix, f.name)
        if not f_path.parent.exists():
            f_path.parent.mkdir(exist_ok=True, parents=True)

        with open(f_path, 'wb') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        file_obj = File(name=f.name, size=f.size, prefix=prefix, content_type=f.content_type)
        file_objs.append(file_obj)

    with atomic():
        objs = File.objects.bulk_create(file_objs)
        BucketAndFile.objects.bulk_create(
            [BucketAndFile(bid=bucket.bid, fid=obj.fid) for obj in objs])

    return JsonResponse({
        "errcode": 0,
        "msg": "上传成功"
    })


# @require_login
@require_GET
def get_file(req):
    bucket_name = req.GET.get("bucket", None)
    fid = req.GET.get("fid", None)
    # uid = req.uid

    try:
        bucket = Bucket.objects.get(name=bucket_name)
        # UserAndBucket.objects.get(uid=uid, bid=bucket.bid)
        BucketAndFile.objects.get(fid=fid, bid=bucket.bid)

    except Bucket.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "该bucket不存在"
        })
    except UserAndBucket.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "该bucket不属于你"
        })
    except BucketAndFile.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "bucket中不存在该文件"
        })

    f = File.objects.get(fid=fid)
    f_path = settings.BASE_DIR.joinpath("media/buckets", bucket_name, f.prefix, f.name)

    def file_iterator(path):
        with open(path, mode='rb') as f:
            while True:
                c = f.read(1024 * 4)
                if c:
                    yield c
                else:
                    break

    resp = StreamingHttpResponse(file_iterator(f_path))
    resp['Content-Type'] = 'application/octet-stream'
    resp['Content-Disposition'] = 'attachment;filename={}'.format(f.name)
    resp['Access-Control-Allow-Origin'] = bucket.allow_origins
    resp['Cache-Control'] = "public, max-age=" + str(bucket.max_age)

    return resp


@require_login
@require_GET
def del_file(req):
    bucket_name = req.GET.get("bucket", None)
    fid = req.GET.get("fid", None)
    uid = req.uid

    try:
        bucket = Bucket.objects.get(name=bucket_name)
        UserAndBucket.objects.get(uid=uid, bid=bucket.bid)
        bucket_and_file = BucketAndFile.objects.get(fid=fid, bid=bucket.bid)
        file = File.objects.get(fid=fid)

        with atomic():
            bucket_and_file.delete()
            file.delete()

        return JsonResponse({
            "errcode": 0,
            "msg": "删除成功"
        })

    except Bucket.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "该bucket不存在"
        })
    except UserAndBucket.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "该bucket不属于你"
        })
    except BucketAndFile.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "bucket中不存在该文件"
        })

    except File.DoesNotExist:
        return JsonResponse({
            "errcode": -1,
            "msg": "该文件不存在"
        })
