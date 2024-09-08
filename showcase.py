import json
import os
import urllib.error
import urllib.request

import aiohttp
import server
from aiohttp import web

BIZYAIR_DEBUG = os.getenv("BIZYAIR_DEBUG", False)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

SHOW_CASES = {}


async def get_bizyair_news(base_url="https://bizyair.siliconflow.cn"):
    url = f"{base_url}/bznews.json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.text()
                    return json.loads(data)
                else:
                    print(f"Failed to fetch news.json: HTTP Status {response.status}")
                    return {}
    except aiohttp.ClientError as e:
        print(f"Error fetching news.json: {e}")
        return {}
    except Exception as e:
        print(f"Error fetching BizyAir bznews.json: {str(e)}")
        return {}


with open(os.path.join(CURRENT_DIR, "bizyair_example_menu.json"), "r") as file:
    SHOW_CASES.update(json.load(file))


def extract_files(data):
    file_whitelist = []
    for key, value in data.items():
        if isinstance(value, dict):
            file_whitelist.extend(extract_files(value))
        else:
            file_whitelist.append(value)
    return file_whitelist


file_whitelist = extract_files(SHOW_CASES)

from server import PromptServer


@PromptServer.instance.routes.get("/bizyair/showcases")
async def set_api_key_page(request):
    return web.Response(
        text=json.dumps(SHOW_CASES, ensure_ascii=False), content_type="application/json"
    )


@PromptServer.instance.routes.get("/bizyair/news")
async def list_news(request):
    return web.Response(
        text=json.dumps(await get_bizyair_news(), ensure_ascii=False),
        content_type="application/json",
    )


@PromptServer.instance.routes.post("/bizyair/workflow")
async def get_file_content(request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.Response(
            text=json.dumps({"error": "Invalid JSON body"}),
            status=400,
            content_type="application/json",
        )

    filename = data.get("file")
    if not filename:
        return web.Response(
            text=json.dumps({"error": "Missing file parameter"}),
            status=400,
            content_type="application/json",
        )

    if filename not in file_whitelist:
        return web.Response(
            text=json.dumps({"error": "Filename not allowed"}),
            status=400,
            content_type="application/json",
        )

    file_path = os.path.join(CURRENT_DIR, "examples", filename)
    if BIZYAIR_DEBUG:
        print(f"request the json workflow: {file_path}")
    if not os.path.isfile(file_path):
        return web.Response(
            text=json.dumps({"error": "File not found"}),
            status=404,
            content_type="application/json",
        )

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = json.load(file)
            return web.Response(
                text=json.dumps(file_content, ensure_ascii=False),
                content_type="application/json",
            )
    except Exception as e:
        return web.Response(
            text=json.dumps({"error": str(e)}),
            status=500,
            content_type="application/json",
        )
