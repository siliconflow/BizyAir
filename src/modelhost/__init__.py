import json
import os
from pathlib import Path
import urllib.request
from aiohttp import web

from server import PromptServer
import bizyair
import bizyair.common

current_path = os.path.abspath(os.path.dirname(__file__))
prompt_server = PromptServer.instance

BIZYAIR_SERVER_ADDRESS = os.getenv(
    "BIZYAIR_SERVER_ADDRESS", "https://api.siliconflow.cn"
)


def _get_modelserver_list(api_key, model_type="bizyair/lora"):
    api_url = f"{BIZYAIR_SERVER_ADDRESS}/supernode/listmodelserver"

    payload = {
        "api_key": api_key,
        "model_type": model_type,
        "secret": "6x7=42",
    }
    auth = f"Bearer {api_key}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": auth,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            response = response.read().decode("utf-8")
        ret = json.loads(response)

        if "result" in ret:  # cloud
            msg = json.loads(ret["result"])
        else:  # local
            msg = ret
        return msg["data"]
    except Exception as e:
        print(f"fail to list model: {str(e)}")
        return []


def get_html_content(filename: str):
    html_file_path = Path(current_path) / filename
    with open(html_file_path, "r", encoding="utf-8") as htmlfile:
        html_content = htmlfile.read()
    return html_content


select_and_upload_model_html = get_html_content("select_and_upload_model.html")


@prompt_server.routes.get("/bizyair/modelhost/select")
async def modelhost_select(request):
    return web.Response(text=select_and_upload_model_html, content_type="text/html")


@prompt_server.routes.post("/bizyair/modelhost/upload")
async def modelhost_upload(request):
    data = await request.json()
    print(data)

    # upload models to siliconcloud server ...
    return web.Response(text="{'status': 'ok'}", content_type="text/json")


list_model_html = get_html_content("list_model.html")


@prompt_server.routes.get("/bizyair/modelhost/list")
async def modelhost_list(request):
    return web.Response(text=list_model_html, content_type="text/html")


@prompt_server.routes.post("/bizyair/modelhost/list")
async def modelhost_getlist(request):
    params = await request.json()
    print(f"parrsm: {params}")
    models_list = _get_modelserver_list(bizyair.common.get_api_key())
    label_list = [item["label_path"] for item in models_list]
    print(str(label_list))
    return web.Response(text=json.dumps(label_list), content_type="text/json")
