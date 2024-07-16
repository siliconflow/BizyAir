import uuid
import os
import configparser
import server
from aiohttp import web

from .utils import validate_api_key

API_KEY = None


@server.PromptServer.instance.routes.post("/bizyair/set_api_key")
async def set_api_key(request):
    global API_KEY
    data = await request.post()
    api_key = data.get("api_key")

    try:
        if api_key:
            response = web.Response(text="ok")
            response.set_cookie("api_key", api_key)
            API_KEY = api_key
            return response
        else:
            return web.Response(text="No token provided", status=400)
    except Exception as e:
        return web.Response(text=str(e), status=500)

@server.PromptServer.instance.routes.get("/bizyair/get_api_key")
async def get_api_key(request):
    global API_KEY
    # 检查是否存在 api_key.ini，文件中是否存在 key
    api_key = ''
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, 'api_key.ini')
    if os.path.exists(file_path):
        config = configparser.ConfigParser()
        config.read(file_path)
        api_key = config.get('auth', 'api_key', fallback='')
        # print(f"api_key from file = {api_key}")
    if api_key=='':
        api_key = request.cookies.get("api_key")
    # print(f"api_key = {api_key}")
    try:
        if api_key:
            API_KEY = api_key
            response = web.Response(text="ok")
            response.set_cookie("api_key", api_key)
            return response
        else:
            return web.Response(text="No api key found in cookie", status=404)
    except Exception as e:
        return web.Response(text="str(e)", status=500)


class SetAPIKey:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"API_KEY": ("STRING", {"default": "YOUR_API_KEY"}),}}

    RETURN_TYPES = ()
    FUNCTION = "set_api_key"

    CATEGORY = "☁️BizyAir"
    OUTPUT_NODE = True

    def set_api_key(self, API_KEY="YOUR_API_KEY"):
        validate_api_key(API_KEY)
        return {"ui": {"api_key": (API_KEY,)}, "result": ()}

    @classmethod
    def IS_CHANGED(s, latent):
        return uuid.uuid4().hex


NODE_CLASS_MAPPINGS = {
    "BizyAirSetAPIKey": SetAPIKey,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirSetAPIKey": "☁️Set SiliconCloud API Key",
}
