import os
import uuid
from pathlib import Path

import server
from aiohttp import web

import bizyair
from bizyair.common import load_api_key, create_api_key_file


API_KEY = None
html_file_path = Path(os.path.dirname(os.path.abspath(__file__))) / "set_api_key.html"
with open(html_file_path, "r", encoding="utf-8") as htmlfile:
    set_api_key_html = htmlfile.read()


has_key, api_key = load_api_key()
if has_key:
    API_KEY = api_key


@server.PromptServer.instance.routes.get("/bizyair/set-api-key")
async def set_api_key_page(request):
    return web.Response(text=set_api_key_html, content_type="text/html")


@server.PromptServer.instance.routes.post("/bizyair/set_api_key")
async def set_api_key(request):
    global API_KEY
    has_key, api_key = load_api_key()
    if has_key:
        API_KEY = api_key
        bizyair.set_api_key(API_KEY)
        return web.Response(text="Key has been loaded from the api_key.ini file")
    data = await request.post()
    api_key = data.get("api_key")
    try:
        if api_key:
            response = web.Response(text="ok")
            response.set_cookie("api_key", api_key, max_age=30 * 24 * 60 * 60)
            API_KEY = api_key
            bizyair.set_api_key(API_KEY)
            return response
        else:
            return web.Response(
                text="No token provided, please refer to cloud.siliconflow.cn to get the key",
                status=400,
            )
    except Exception as e:
        return web.Response(text=str(e), status=500)


@server.PromptServer.instance.routes.get("/bizyair/get_api_key")
async def get_api_key(request):
    global API_KEY
    has_key, api_key = load_api_key()
    if has_key:
        API_KEY = api_key
        bizyair.set_api_key(API_KEY)
        return web.Response(text="Key has been loaded from the api_key.ini file")

    if not has_key:
        api_key = request.cookies.get("api_key")
    try:
        if api_key:
            API_KEY = api_key
            response = web.Response(text="ok")
            bizyair.set_api_key(API_KEY)
            return response
        else:
            return web.Response(
                text="No api key found in cookie, please refer to cloud.siliconflow.cn to get the key",
                status=404,
            )
    except Exception as e:
        return web.Response(text="str(e)", status=500)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
