import glob
import hashlib
import json
import os
import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class CacheConfig:
    max_size: int = 100
    expiration: int = 300  # 300 seconds
    cache_dir: str = "./cache"
    file_prefix: str = "bizyair_cache_"
    file_suffix: str = ".json"
    use_cache: bool = True

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        return cls(
            max_size=config.get("max_size", 100),
            expiration=config.get("expiration", 300),
            cache_dir=config.get("cache_dir", "./cache"),
            file_prefix=config.get("file_prefix", "bizyair_cache_"),
            file_suffix=config.get("file_suffix", ".json"),
            use_cache=config.get("use_cache", True),
        )


class CacheManager(ABC):
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def disable(self):
        pass


class ConfigSingleton:
    _instance_lock = threading.Lock()
    _instances = {}

    def __new__(cls, config, *args, **kwargs):
        config_str = str(config)
        config_key = hashlib.sha256(config_str.encode()).hexdigest()
        if config_key not in cls._instances:
            with cls._instance_lock:
                if config_key not in cls._instances:
                    instance = super().__new__(cls)
                    cls._instances[config_key] = instance

        return cls._instances[config_key]


class BizyAirTaskCache(ConfigSingleton, CacheManager):
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache = OrderedDict()
        self.cache_dir = config.cache_dir
        self.ensure_directory_exists()
        self.cache = self.load_cache() if config.use_cache else self.cache

    def ensure_directory_exists(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def load_cache(self):
        cache_v_files = glob.glob(
            os.path.join(
                self.cache_dir, f"{self.config.file_prefix}*{self.config.file_suffix}"
            )
        )
        output = OrderedDict()
        cache_datas = []
        for cache_file in cache_v_files:
            try:
                file_name = os.path.basename(cache_file)[
                    len(self.config.file_prefix) : -len(self.config.file_suffix)
                ]
                cache_key = file_name.split("-")[0]
                cache_timestamp = file_name.split("-")[1]
                if int(time.time()) - int(cache_timestamp) > self.config.expiration:
                    self.delete_file(cache_file)
                    continue
                cache_datas.append(
                    {
                        "key": cache_key,
                        "timestamp": int(cache_timestamp),
                        "file_path": cache_file,
                    }
                )
            except Exception as e:
                print(
                    f"Warning: Error loading cache file {cache_file}: because {e}, will delete it"
                )
        cache_datas = sorted(cache_datas, key=lambda x: x["timestamp"])
        for cache_data in cache_datas:
            output[cache_data["key"]] = (
                cache_data["file_path"],
                cache_data["timestamp"],
            )
        return output

    def delete(self, key):
        if key in self.cache:
            self.delete_file(self.cache[key][0])
            del self.cache[key]

    def get(self, key):
        if key not in self.cache:
            return None

        file_path, timestamp = self.cache[key]
        if time.time() - timestamp >= self.config.expiration:
            self._remove_expired_entry(file_path, key)
            return None

        cache_data = self._read_file(file_path)
        if cache_data["cache_key"] == key:
            return cache_data["result"]
        else:
            self._remove_expired_entry(file_path, key)
            return None

    def _read_file(self, file_path):
        try:
            with open(file_path, "r") as f:
                cache_data = json.load(f)
                return cache_data
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
        return None

    def _remove_expired_entry(self, file_path, key):
        self.delete_file(file_path)
        del self.cache[key]

    def set(self, key, value, *, overwrite=False):
        if not overwrite and key in self.cache:
            raise ValueError(
                f"Key '{key}' already exists in cache. Use overwrite=True to replace it."
            )
        assert isinstance(key, str), "Key must be a string"

        if len(self.cache) >= self.config.max_size:
            self._evict_oldest()

        timestamp = int(time.time())
        file_path = os.path.join(
            self.cache_dir, f"{self.config.file_prefix}{key}-{timestamp}.json"
        )
        self.write_file(key, value, file_path, timestamp)

    def _evict_oldest(self):
        oldest_key, (oldest_file_path, _) = self.cache.popitem(last=False)
        self.delete_file(oldest_file_path)

    def write_file(self, key: str, value: Any, file_path: str, timestamp: int):
        try:
            with open(file_path, "w") as f:
                json.dump(
                    {"result": value, "cache_key": key, "timestamp": timestamp}, f
                )
            self.cache[key] = (file_path, timestamp)
        except Exception as e:
            print(f"Error writing file for key '{key}': {e}")

    def delete_file(self, file_path):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file '{file_path}': {e}")

    def clear(self):
        for file_path, _ in self.cache.values():
            self.delete_file(file_path)
        self.cache.clear()

    def disable(self):
        self.clear()


# Example usage
if __name__ == "__main__":
    cache_config = CacheConfig(max_size=12, expiration=10, cache_dir="./cache")
    cache = BizyAirTaskCache(cache_config)
    assert (
        BizyAirTaskCache(CacheConfig(max_size=12, expiration=10, cache_dir="./cache"))
        is cache
    )

    # Set some cache values
    cache.set("key1", "This is the value for key1")
    cache.set("key2", "This is the value for key2")

    # Retrieve values from cache
    print(cache.get("key1"))  # Output: This is the value for key1
    print(cache.get("key2"))  # Output: This is the value for key2

    # Wait for expiration
    time.sleep(9)
    print(cache.get("key1"))  # Output: None (expired)

    # Clear cache
    cache.clear()
    print(cache.get("key2"))  # Output: None (cache cleared)
