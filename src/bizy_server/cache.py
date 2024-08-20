import functools
import json
import threading


class UploadCache:
    _lock = threading.Lock()

    def __init__(self):
        self._cache = {}  # 用于存储缓存数据

    @staticmethod
    def _with_lock(func):
        """装饰器，用于在执行函数前获取锁，并在函数执行后释放锁"""

        def wrapper(*args, **kwargs):
            with UploadCache._lock:
                result = func(*args, **kwargs)
            return result

        return wrapper

    def upload_id_exists(self, upload_id):
        """判断upload_id是否存在"""
        return upload_id in self._cache

    @_with_lock
    def get_valuemap(self, upload_id):
        """根据upload_id获取valuemap"""
        return self._cache.get(upload_id, {})

    @_with_lock
    def get_file_info(self, upload_id, filename):
        """根据upload_id和filename获取字典"""
        valuemap = self._cache.get(upload_id, {})
        return valuemap.get(filename, None)

    @_with_lock
    def set_valuemap(self, upload_id, valuemap):
        """根据upload_id设置valuemap"""
        self._cache[upload_id] = valuemap

    @_with_lock
    def set_file_info(self, upload_id, filename, info):
        """根据upload_id和filename设置字典"""
        if upload_id not in self._cache:
            self._cache[upload_id] = {}
        self._cache[upload_id][filename] = info

    def __str__(self):
        cache_str = "UploadCache(\n"
        for upload_id, valuemap in self._cache.items():
            cache_str += f"  {upload_id}: {{\n"
            for filename, info in valuemap.items():
                cache_str += f"    {json.dumps(filename)}: {json.dumps(info)}\n"
            cache_str += "  }\n"
        cache_str += ")"
        return cache_str
