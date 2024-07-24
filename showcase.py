import json
import os

import server
from aiohttp import web

BIZYAIR_DEBUG = os.getenv("BIZYAIR_DEBUG", False)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

SHOW_CASES = [
    {
        "title": "生成照片风格的图片",
        "summary": "",
        "file": "bizyair_generate_photorealistic_images_workflow.json",
    },
    {
        "title": "Kolors 文生图",
        "summary": "",
        "file": "bizyair_generate_photorealistic_images_workflow.json",
    },
    {
        "title": "抠除背景",
        "summary": "",
        "file": "bizyair_remove_background_workflow.json",
    },
]


@server.PromptServer.instance.routes.get("/bizyair/showcases")
async def set_api_key_page(request):
    return web.Response(text=json.dumps(SHOW_CASES, ensure_ascii=False), content_type="application/json")

@server.PromptServer.instance.routes.get("/bizyair/workflow")
async def get_file_content(request):
    filename = request.rel_url.query.get("file")
    if not filename:
        return web.Response(text=json.dumps({"error": "Missing file parameter"}), status=400, content_type="application/json")

    file_path = os.path.join(CURRENT_DIR, "examples", filename)
    if BIZYAIR_DEBUG:
        print(f"request the json workflow: {file_path}")
    if not os.path.isfile(file_path):
        return web.Response(text=json.dumps({"error": "File not found"}), status=404, content_type="application/json")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = json.load(file)
            return web.Response(text=json.dumps(file_content, ensure_ascii=False), content_type="application/json")
    except Exception as e:
        return web.Response(text=json.dumps({"error": str(e)}), status=500, content_type="application/json")
