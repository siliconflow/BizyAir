import configparser
import os

bizyair_key = os.getenv("BIZYAIR_KEY", "")
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
config = configparser.ConfigParser()
config["auth"] = {"api_key": bizyair_key}
with open(os.path.join(current_directory, "..", "api_key.ini"), "w") as configfile:
    config.write(configfile)
