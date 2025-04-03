import configparser
import os
import shutil

from .errno import errnos


class UserProfile:
    def __init__(self):
        UserProfile.instance = self

        self.profile_cache = {}
        self.load_profile()
        self.lang = "zh"

    def getLang(self):
        return self.lang

    def getAll(self):
        return self.profile_cache

    def load_profile(self):
        """加载用户配置文件到缓存"""
        profile_path = os.path.join(os.getenv("BIZYAIR_COMFYUI_PATH"), "profile.ini")
        example_path = os.path.join(
            os.path.dirname(profile_path), "profile.ini.example"
        )

        # 如果配置文件不存在且示例文件存在，则复制示例文件
        if not os.path.exists(profile_path) and os.path.exists(example_path):
            try:
                shutil.copy2(example_path, profile_path)
            except Exception as e:
                print(
                    f"\033[31m[BizyAir]\033[0m Fail to copy example profile: {str(e)}"
                )
                return

        # 如果配置文件仍不存在，则创建默认配置
        if not os.path.exists(profile_path):
            try:
                config = configparser.ConfigParser()
                config.add_section("global")
                config.set("global", "lang", "zh")
                with open(profile_path, "w") as f:
                    config.write(f)
            except Exception as e:
                print(
                    f"\033[31m[BizyAir]\033[0m Fail to create default profile: {str(e)}"
                )
                return

        try:
            config = configparser.ConfigParser()
            config.read(profile_path)
            self.profile_cache = {}
            for section in config.sections():
                self.profile_cache[section] = {}
                for key, value in config.items(section):
                    self.profile_cache[section][key] = value

            if self.profile_cache["global"]["lang"]:
                self.lang = self.profile_cache["global"]["lang"]
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to read profile: {str(e)}")

    def update_profile(self, json_data):
        profile_path = os.path.join(os.getenv("BIZYAIR_COMFYUI_PATH"), "profile.ini")
        try:
            config = configparser.ConfigParser()
            if os.path.exists(profile_path):
                config.read(profile_path)

            for section, values in json_data.items():
                if not config.has_section(section):
                    config.add_section(section)
                for key, value in values.items():
                    config.set(section, key, str(value))

            with open(profile_path, "w") as f:
                config.write(f)

            # 重新加载配置
            self.load_profile()
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to write profile: {str(e)}")
            return errnos.WRITE_PROFILE_FAILED


user_profile = UserProfile()
