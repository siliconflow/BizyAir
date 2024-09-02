import configparser
import os
from os import environ
from pathlib import Path


def env(key, type_, default=None):
    if key not in environ:
        return default

    val = environ[key]

    if type_ == str:
        return val
    if type_ == bool:
        if val.lower() in ["1", "true", "yes", "y", "ok", "on"]:
            return True
        if val.lower() in ["0", "false", "no", "n", "nok", "off"]:
            return False
        raise ValueError(
            "Invalid environment variable '%s' (expected a boolean): '%s'" % (key, val)
        )
    if type_ == int:
        try:
            return int(val)
        except ValueError:
            raise ValueError(
                "Invalid environment variable '%s' (expected an integer): '%s'"
                % (key, val)
            ) from None
    raise ValueError("The requested type '%r' is not supported" % type_)


def load_api_key():

    file_path = Path(os.path.abspath(__file__)).parents[3] / "api_key.ini"

    if file_path.is_file() and file_path.exists():
        config = configparser.ConfigParser()
        config.read(file_path)
        api_key: str = config.get("auth", "api_key", fallback="").strip().strip("'\"")
        has_key = api_key.startswith("sk-")
        return has_key, api_key
    else:
        return False, "Key not found, please refer to cloud.siliconflow.cn"


def create_api_key_file(api_key):
    config = configparser.ConfigParser()
    config["auth"] = {"api_key": api_key}
    file_path = Path(os.path.abspath(__file__)).parents[3] / "api_key.ini"
    try:
        with open(file_path, "w", encoding="utf-8") as configfile:
            config.write(configfile)
    except Exception as e:
        raise Exception(f"An error occurred when save the key: {e}")


BIZYAIR_API_KEY = env("BIZYAIR_API_KEY", str, load_api_key()[1])
# Development Settings
BIZYAIR_DEV_REQUEST_URL = env("BIZYAIR_DEV_REQUEST_URL", str, None)
BIZYAIR_DEBUG = env("BIZYAIR_DEBUG", bool, False)
