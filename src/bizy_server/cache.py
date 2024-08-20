import threading


class UploadCache:
    def __init__(self):
        self._cache = {}  # 用于存储缓存数据
        self._lock = threading.Lock()  # 用于线程同步的锁

    def _with_lock(self, func):
        """装饰器，用于在执行函数前获取锁，并在函数执行后释放锁"""
        def wrapper(*args, **kwargs):
            with self._lock:
                return func(*args, **kwargs)
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