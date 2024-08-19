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


list_model_html = get_html_content("templates/list_model.html")


@prompt_server.routes.get("/bizyair/modelhost/list")
async def modelhost_list(request):
    return web.Response(text=list_model_html, content_type="text/html")
