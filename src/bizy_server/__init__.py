import json
import os
from pathlib import Path
import urllib.request
import urllib.parse
from aiohttp import web

from server import PromptServer
import bizyair
import bizyair.common
from .errno import ErrorNo, CODE_OK, INVAILD_TYPE, INVAILD_NAME, CHECK_MODEL_EXISTS_ERR, NO_FILE_UPLOAD_ERR, \
    EMPTY_UPLOAD_ID_ERR

# from .cache import UploadCache

current_path = os.path.abspath(os.path.dirname(__file__))
prompt_server = PromptServer.instance

BIZYAIR_SERVER_ADDRESS = os.getenv(
    "BIZYAIR_SERVER_ADDRESS", "https://uat-bizyair-api.siliconflow.cn"
)

API_PREFIX = "bizyair/modelhost"


# CACHE = UploadCache()


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
upload_model_html = get_html_content("templates/upload_model.html")


@prompt_server.routes.get(f"/{API_PREFIX}/list")
async def forward_list_model_html(request):
    return web.Response(text=list_model_html, content_type="text/html")


@prompt_server.routes.get(f"/{API_PREFIX}/upload")
async def forward_upload_model_html(request):
    return web.Response(text=upload_model_html, content_type="text/html")


@prompt_server.routes.post(f"/{API_PREFIX}/check_model_exists")
async def check_model_exists(request):
    json_data = await request.json()
    if "type" not in json_data:
        return ErrResponse(INVAILD_TYPE)

    type = json_data["type"]
    if not is_string_valid(type):
        return ErrResponse(INVAILD_TYPE)

    if type not in ["bizyair/lora"]:
        return ErrResponse(INVAILD_TYPE)

    if "name" not in json_data:
        return ErrResponse(INVAILD_NAME)

    name = json_data["name"]
    if not is_string_valid(name):
        return ErrResponse(INVAILD_NAME)

    return check_model(name=name, type=type)


@prompt_server.routes.post(f"/{API_PREFIX}/file_upload")
async def file_upload(request):
    post = await request.post()
    upload_id = post.get("upload_id")
    if not is_string_valid(upload_id):
        return ErrResponse(EMPTY_UPLOAD_ID_ERR)

    file = post.get("file")
    if file and file.file:
        filename = file.filename
        if not filename:
            return ErrResponse(NO_FILE_UPLOAD_ERR)
        full_output_folder = os.path.join(os.path.normpath("bizy_air"), os.path.normpath("localstore"), upload_id)
        filepath = os.path.abspath(os.path.join(full_output_folder, filename))
        parent_folder = os.path.dirname(filepath)
        if not os.path.exists(parent_folder):
            os.makedirs(parent_folder)

        print(f"write file to localstore: upload_id={upload_id}, filepath={filepath}")
        with open(filepath, "wb") as f:
            f.write(file.file.read())
        #
        # if not CACHE.upload_id_exists(upload_id=upload_id):
        #     upload_file_cache = CACHE.get_valuemap(upload_id=upload_id)
        #
        # CACHE.set_file_info(upload_id=upload_id, filename=filename, info={
        #     "relPath": filename,
        #     "size": os.path.getsize(filepath)
        # })

    return JsonResponse(200, {"code": CODE_OK, "message": "success"})


def check_model(type: str, name: str):
    server_url = f"{BIZYAIR_SERVER_ADDRESS}/x/v1/models/check"

    payload = {
        "name": name,
        "type": type,
    }
    headers = auth_header()

    try:
        resp = do_get(server_url, params=payload, headers=headers)
        ret = json.loads(resp)
        print(ret)
        if ret["code"] != CODE_OK:
            return ErrResponse(ErrorNo(500, ret["code"], None, ret["message"]))

        exists = ret["data"]["exists"]
        return JsonResponse(200, {"exists": exists})

    except Exception as e:
        print(f"fail to list model: {str(e)}")
        return ErrResponse(CHECK_MODEL_EXISTS_ERR)


def is_string_valid(s):
    # 检查s是否已经被定义（即不是None）且不是空字符串
    if s is not None and s != "":
        return True
    else:
        return False


def to_slash(path):
    return path.replace('\\', '/')


def JsonResponse(http_status_code, data):
    return web.json_response(data, status=http_status_code, content_type="application/json")


def ErrResponse(err: ErrorNo):
    return JsonResponse(err.http_status_code, {"message": err.message, "code": err.code, "data": err.data})


def auth_header():
    api_key = bizyair.common.get_api_key()
    auth = f"Bearer {api_key}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": auth,
    }
    return headers


def do_get(url, params=None, headers=None):
    # 将字典编码为URL参数字符串
    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"

    # 发送GET请求
    request = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(request) as response:
        return response.read().decode('utf-8')


def do_post(url, data=None, headers=None):
    # 将字典转换为字节串
    if data:
        data = urllib.parse.urlencode(data).encode('utf-8')

    # 创建请求对象
    request = urllib.request.Request(url, data=data, headers=headers, method='POST')

    # 发送POST请求
    with urllib.request.urlopen(request) as response:
        return response.read().decode('utf-8')
