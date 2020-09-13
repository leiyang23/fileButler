from django.apps import AppConfig


class FilemanageConfig(AppConfig):
    name = 'fileManage'

    def ready(self):
        # 1. 建立文件存放的文件夹
        from django.conf import settings
        store_path = settings.BASE_DIR.joinpath("media", "buckets")
        if not store_path.exists():
            store_path.mkdir(exist_ok=True, parents=True)
