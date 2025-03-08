import json
import os
from enum import Enum

from aiohttp import web

BIZYAIR_DEBUG = os.getenv("BIZYAIR_DEBUG", False)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

SHOW_CASES = {}
SAM_COORDINATE = {}
IS_RESET_SAM = False


class EDIT_MODE(Enum):
    box = 0
    point = 1


from server import PromptServer


@PromptServer.instance.routes.post("/bizyair/postsam")
async def save_sam(request):
    global IS_RESET_SAM
    IS_RESET_SAM = False
    post = await request.post()
    SAM_COORDINATE["nums"] = post.get("nums")
    SAM_COORDINATE["mode"] = json.loads(post.get("mode"))
    if SAM_COORDINATE["mode"] == EDIT_MODE.point.value:
        SAM_COORDINATE["point_coords"] = json.loads(post.get("coords"))
    elif SAM_COORDINATE["mode"] == EDIT_MODE.box.value:
        SAM_COORDINATE["box_coords"] = json.loads(post.get("coords"))
    SAM_COORDINATE["filename"] = post.get("filename")

    return web.Response(status=200)


@PromptServer.instance.routes.get("/bizyair/getsam")
async def get_sam(request):
    return web.Response(
        text=json.dumps(SAM_COORDINATE, ensure_ascii=False),
        content_type="application/json",
    )


@PromptServer.instance.routes.get("/bizyair/resetsam")
async def reset_sam(request):
    global IS_RESET_SAM
    IS_RESET_SAM = True
    return web.Response(status=200)


@PromptServer.instance.routes.get("/bizyair/isresetsam")
async def isreset_sam(request):
    status = {"isresetsam": IS_RESET_SAM}
    return web.Response(
        text=json.dumps(status),
        content_type="application/json",
    )
