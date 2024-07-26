import json
import os

import server
from aiohttp import web

BIZYAIR_DEBUG = os.getenv("BIZYAIR_DEBUG", False)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

SHOW_CASES = [
    {
        "title": "Remove the background from the image",
        "file": "bizyair_showcase_remove_background.json",
    },
    {
        "title": "Generate an image from a line drawing",
        "file": "bizyair_showcase_interior_design.json",
    },
    {
        "title": "Recreate an existing image",
        "file": "bizyair_showcase_caption_redraw.json",
    },
    {
        "title": "Design a submarine like a great white shark",
        "file": "bizyair_showcase_shark_submarine.json",
    },
    {
        "title": "All types of ControlNet preprocessors",
        "file": "bizyair_controlnet_preprocessor_workflow.json",
    },
    {
        "title": "Text to Image by BizyAir KSampler",
        "file": "bizyair_showcase_ksampler_txt2img.json",
    },
    {
        "title": "Image to Image by BizyAir KSampler",
        "file": "bizyair_showcase_ksampler_img2img.json",
    },
    {
        "title": "LoRA workflow by BizyAir KSampler",
        "file": "bizyair_showcase_ksampler_lora.json",
    },
    {
        "title": "ControlNet workflow by BizyAir KSampler",
        "file": "bizyair_showcase_ksampler_controlnet.json",
    },
    {
        "title": "IP Adapter workflow by BizyAir KSampler",
        "file": "bizyair_showcase_ksampler_ipadapter.json",
    },
    {
        "title": "Run BizyAir nodes with local nodes",
        "file": "bizyair_showcase_run_with_local_nodes.json",
    },
]

file_whitelist = [item["file"] for item in SHOW_CASES]


@server.PromptServer.instance.routes.get("/bizyair/showcases")
async def set_api_key_page(request):
    return web.Response(
        text=json.dumps(SHOW_CASES, ensure_ascii=False), content_type="application/json"
    )


@server.PromptServer.instance.routes.post("/bizyair/workflow")
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
