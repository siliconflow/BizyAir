import os
import uuid
from pathlib import Path

import bizyengine.core
import server
from aiohttp import web
from bizyengine.core.common import create_api_key_file, load_api_key, validate_api_key

API_KEY = None
# html_file_path = Path(os.path.dirname(os.path.abspath(__file__))) / "set_api_key.html"
# with open(html_file_path, "r", encoding="utf-8") as htmlfile:
#     set_api_key_html = htmlfile.read()


has_key, api_key = load_api_key()
if has_key:
    API_KEY = api_key


# @server.PromptServer.instance.routes.get("/bizyair/set-api-key")
# async def set_api_key_page(request):
#     return web.Response(text=set_api_key_html, content_type="text/html")


@server.PromptServer.instance.routes.post("/bizyair/set_api_key")
async def set_api_key(request):
    global API_KEY
    try:
        data = await request.post()
        api_key = data.get("api_key")
        if api_key:
            if not validate_api_key(api_key):
                error_msg = "Wrong API key provided, please refer to cloud.siliconflow.cn to get the key"
                print("set_api_key:", error_msg)
                return web.Response(
                    text=error_msg,
                    status=400,
                )
            create_api_key_file(api_key)
            API_KEY = api_key
            bizyengine.core.set_api_key(API_KEY, override=True)
            print("Set the key sucessfully.")
            return web.Response(text="ok")
        else:
            error_msg = "No API key provided, please refer to cloud.siliconflow.cn to get the key"
            print("set_api_key:", error_msg)
            return web.Response(
                text=error_msg,
                status=400,
            )
    except Exception as e:
        print(f"set api key error: {str(e)}")
        return web.Response(text=str(e), status=500)


@server.PromptServer.instance.routes.get("/bizyair/get_api_key")
async def get_api_key(request):
    global API_KEY
    try:
        has_key, api_key = load_api_key()
        if has_key:
            API_KEY = api_key
            bizyengine.core.set_api_key(API_KEY)
            return web.Response(text="Key has been loaded from the api_key.ini file")
        else:
            api_key = request.cookies.get("api_key")
            if not api_key:
                print("No api key found in cookies")
                return web.Response(
                    text="No api key found in cookies, please refer to cloud.siliconflow.cn to get the key",
                    status=404,
                )
            API_KEY = api_key
            bizyengine.core.set_api_key(API_KEY)
            return web.Response(text="Key has been loaded from the cookies")

    except Exception as e:
        return web.Response(text=str(e), status=500)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
