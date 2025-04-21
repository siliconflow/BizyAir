import os
import uuid
from pathlib import Path

import bizyengine.core
import bizyengine.core.common
import server
from aiohttp import web

# html_file_path = Path(os.path.dirname(os.path.abspath(__file__))) / "set_api_key.html"
# with open(html_file_path, "r", encoding="utf-8") as htmlfile:
#     set_api_key_html = htmlfile.read()


# @server.PromptServer.instance.routes.get("/bizyair/set-api-key")
# async def set_api_key_page(request):
#     return web.Response(text=set_api_key_html, content_type="text/html")


@server.PromptServer.instance.routes.post("/bizyair/set_api_key")
async def set_api_key(request):
    try:
        data = await request.post()
        api_key = data.get("api_key")
        if api_key:
            if not bizyengine.core.set_api_key(api_key, True):
                error_msg = "Wrong API key provided, please refer to cloud.siliconflow.cn to get the key"
                print("set_api_key:", error_msg)
                return web.Response(
                    text=error_msg,
                    status=400,
                )
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
    try:
        if bizyengine.core.common.get_api_key():
            print("test test test")
            return web.Response(text="Key has been loaded from the api_key.ini file")
        else:
            api_key = request.cookies.get("api_key")
            if not api_key:
                print("No api key found in cookies")
                return web.Response(
                    text="No api key found in cookies, please refer to cloud.siliconflow.cn to get the key",
                    status=404,
                )
            if bizyengine.core.set_api_key(api_key):
                return web.Response(text="Key has been loaded from the cookies")
            return web.Response(text="Cannot set api key", status=500)

    except Exception as e:
        return web.Response(text=str(e), status=500)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
