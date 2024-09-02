import base64
import hashlib
import json
import logging
import os
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

import crcmod
import oss2
from aiohttp import web
from server import PromptServer

import bizyair
import bizyair.common

from .cache import UploadCache
from .errno import (
    INVALID_API_KEY,
    CHECK_MODEL_EXISTS_ERR,
    CODE_NO_MODEL_FOUND,
    CODE_OK,
    COMMIT_FILE_ERR,
    COMMIT_MODEL_ERR,
    DELETE_MODEL_ERR,
    EMPTY_FILES_ERR,
    EMPTY_UPLOAD_ID_ERR,
    INVALID_FILENAME_ERR,
    INVALID_NAME,
    INVALID_TYPE,
    INVALID_UPLOAD_ID_ERR,
    LIST_MODEL_FILE_ERR,
    MODEL_ALREADY_EXISTS_ERR,
    NO_FILE_UPLOAD_ERR,
    SIGN_FILE_ERR,
    UPLOAD_ERR,
    ErrorNo,
)
from .oss import AliOssStorageClient

current_path = os.path.abspath(os.path.dirname(__file__))
prompt_server = PromptServer.instance

BIZYAIR_SERVER_ADDRESS = os.getenv(
    "BIZYAIR_SERVER_ADDRESS", "https://uat-bizyair-api.siliconflow.cn"
)

API_PREFIX = "bizyair/modelhost"

CACHE = UploadCache()
logging.basicConfig(level=logging.DEBUG)

TYPE_OPTIONS = {
    "checkpoint": "bizyair/lora",
    "lora": "bizyair/lora",
    "vae": "bizyair/vae",
    "controlnet": "bizyair/controlnet",
    "other": "other",
}
ALLOW_TYPES = list(TYPE_OPTIONS.values())


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


@prompt_server.routes.get(f"/{API_PREFIX}/model_types")
async def list_model_types(request):
    types = []
    for k, v in TYPE_OPTIONS.items():
        types.append({"label": k, "value": v})

    return OKResponse(types)


@prompt_server.routes.post(f"/{API_PREFIX}/check_model_exists")
async def check_model_exists(request):
    json_data = await request.json()
    err = check_type(json_data)
    if err is not None:
        return err

    err = check_str_param(json_data, param_name="name", err=INVALID_TYPE)
    if err is not None:
        return err

    exists, err = check_model(name=json_data["name"], type=json_data["type"])
    if err is not None:
        return ErrResponse(err)

    return OKResponse({"exists": exists})


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
        full_output_folder = os.path.join(
            os.path.normpath("bizy_air"), os.path.normpath("localstore"), upload_id
        )
        filepath = os.path.abspath(os.path.join(full_output_folder, filename))
        parent_folder = os.path.dirname(filepath)
        if not os.path.exists(parent_folder):
            os.makedirs(parent_folder)

        with open(filepath, "wb") as f:
            f.write(file.file.read())

        sha256sum = calculate_hash(filepath)
        print(
            f"write file to localstore: upload_id={upload_id}, filepath={filepath}, signature={sha256sum}"
        )

        if not CACHE.upload_id_exists(upload_id=upload_id):
            CACHE.set_valuemap(upload_id=upload_id, valuemap={})

        CACHE.set_file_info(
            upload_id=upload_id,
            filename=filename,
            info={
                "relPath": to_slash(filename),
                "size": os.path.getsize(filepath),
                "signature": sha256sum,
            },
        )

        sign_data, err = sign(sha256sum)
        file_record = sign_data.get("file")
        if err is not None:
            return ErrResponse(err)

        if is_string_valid(file_record.get("id")):
            file_info = CACHE.get_file_info(upload_id=upload_id, filename=filename)
            file_info["id"] = file_record.get("id")
            file_info["remote_key"] = file_record.get("object_key")
            file_info["progress"] = "100.00%"
        else:
            print("start uploading file")
            file_storage = sign_data.get("storage")
            try:

                def updateProgress(consume_bytes, total_bytes):
                    print(f"uploading: {consume_bytes}/{total_bytes}")
                    fi = CACHE.get_file_info(upload_id=upload_id, filename=filename)
                    if fi is not None:
                        fi["progress"] = "{:.2f}%".format(
                            consume_bytes / total_bytes * 100
                        )

                oss_client = AliOssStorageClient(
                    endpoint=file_storage.get("endpoint"),
                    bucket_name=file_storage.get("bucket"),
                    access_key=file_record.get("access_key_id"),
                    secret_key=file_record.get("access_key_secret"),
                    security_token=file_record.get("security_token"),
                    onUploading=updateProgress,
                )
                oss_client.upload_file(filepath, file_record.get("object_key"))
            except oss2.exceptions.OssError as e:
                print(f"OSS err:{str(e)}")
                return ErrResponse(UPLOAD_ERR)

            commit_data, err = commit_file(
                signature=sha256sum, object_key=file_record.get("object_key")
            )
            if err is not None:
                return ErrResponse(err)
            new_file_record = commit_data.get("file")
            file_info = CACHE.get_file_info(upload_id=upload_id, filename=filename)
            file_info["id"] = new_file_record.get("id")
            file_info["remote_key"] = new_file_record.get("object_key")
            print(f"{file_info['relPath']} Already Uploaded")

        if os.path.exists(filepath):
            # 删除文件
            os.remove(filepath)

        file_info = CACHE.get_file_info(upload_id=upload_id, filename=filename)
        return OKResponse({"sign": file_info["signature"]})
    else:
        return ErrResponse(NO_FILE_UPLOAD_ERR)


@prompt_server.routes.post(f"/{API_PREFIX}/model_upload")
async def upload_model(request):
    json_data = await request.json()
    err = check_str_param(json_data, "upload_id", EMPTY_UPLOAD_ID_ERR)
    if err is not None:
        return err

    if not CACHE.upload_id_exists(json_data["upload_id"]):
        return ErrResponse(INVALID_UPLOAD_ID_ERR)

    err = check_type(json_data)
    if err is not None:
        return err

    err = check_str_param(json_data, "name", INVALID_NAME)
    if err is not None:
        return err

    exists, err = check_model(type=json_data["type"], name=json_data["name"])
    if err is not None:
        return err

    if exists and "overwrite" not in json_data or json_data["overwrite"] is not True:
        return ErrResponse(MODEL_ALREADY_EXISTS_ERR)

    if "files" not in json_data or len(json_data["files"]) < 1:
        return ErrResponse(EMPTY_FILES_ERR)

    files = json_data["files"]
    for file in files:
        file["path"] = to_slash(file["path"])

    commit_ret, err = commit_model(
        model_files=files,
        model_name=json_data["name"],
        model_type=json_data["type"],
        overwrite=json_data["overwrite"],
    )
    if err is not None:
        return ErrResponse(err)

    print("Uploaded successfully")
    return OKResponse(None)


@prompt_server.routes.get(f"/{API_PREFIX}/models/files")
async def list_model_files(request):
    err = check_type(request.rel_url.query)
    if err is not None:
        return err

    payload = {
        "type": request.rel_url.query["type"],
    }

    if "name" in request.rel_url.query:
        payload["name"] = request.rel_url.query["name"]

    if "ext_name" in request.rel_url.query:
        payload["ext_name"] = request.rel_url.query["ext_name"]

    headers, err = auth_header()
    if err is not None:
        return err

    server_url = f"{BIZYAIR_SERVER_ADDRESS}/x/v1/models/files"

    try:
        resp = do_get(server_url, params=payload, headers=headers)
        ret = json.loads(resp)
        if ret["code"] != CODE_OK:
            if ret["code"] == CODE_NO_MODEL_FOUND:
                return OKResponse([])
            else:
                return ErrResponse(ErrorNo(500, ret["code"], None, ret["message"]))

        if not ret["data"]:
            return OKResponse([])

        files = ret["data"]["files"]
        result = []
        if len(files) > 0:
            tree = defaultdict(lambda: {"name": "", "list": []})

            for item in files:
                parts = item["label_path"].split("/")
                model_name = parts[0]
                if model_name not in tree:
                    tree[model_name] = {"name": model_name, "list": [item]}
                else:
                    tree[model_name]["list"].append(item)
            result = list(tree.values())

        return OKResponse(result)

    except Exception as e:
        print(f"fail to list model files: {str(e)}")
        return ErrResponse(LIST_MODEL_FILE_ERR)


@prompt_server.routes.get(f"/{API_PREFIX}/file_upload/progress")
async def file_upload_progress(request):
    if "upload_id" not in request.rel_url.query:
        return ErrResponse(INVALID_UPLOAD_ID_ERR)
    if "filename" not in request.rel_url.query:
        return ErrResponse(INVALID_FILENAME_ERR)

    upload_id = request.rel_url.query["upload_id"]
    filename = request.rel_url.query["filename"]

    file_info = CACHE.get_file_info(upload_id=upload_id, filename=filename)
    if file_info is not None:
        if "progress" in file_info:
            return JsonResponse({"progress": file_info["progress"]})

    return JsonResponse({"progress": "0.00%"})


@prompt_server.routes.delete(f"/{API_PREFIX}/models")
async def delete_model(request):
    json_data = await request.json()

    err = check_type(json_data)
    if err is not None:
        return err

    err = check_str_param(json_data, "name", INVALID_NAME)
    if err is not None:
        return err

    err = remove_model(model_type=json_data["type"], model_name=json_data["name"])
    if err is not None:
        return err

    print("Delete successfully")
    return OKResponse(None)


def check_model(type: str, name: str) -> (bool, ErrorNo):
    server_url = f"{BIZYAIR_SERVER_ADDRESS}/x/v1/models/check"

    payload = {
        "name": name,
        "type": type,
    }
    headers, err = auth_header()
    if err is not None:
        return err

    try:
        resp = do_get(server_url, params=payload, headers=headers)
        ret = json.loads(resp)
        if ret["code"] != CODE_OK:
            return ErrorNo(500, ret["code"], None, ret["message"])

        if "exists" not in ret["data"]:
            return False, None

        return True, None

    except Exception as e:
        print(f"fail to check model: {str(e)}")
        return None, CHECK_MODEL_EXISTS_ERR


def sign(signature: str) -> (dict, ErrorNo):
    server_url = f"{BIZYAIR_SERVER_ADDRESS}/x/v1/files/{signature}"
    headers, err = auth_header()
    if err is not None:
        return err

    try:
        resp = do_get(server_url, params=None, headers=headers)
        ret = json.loads(resp)
        if ret["code"] != CODE_OK:
            return None, ErrorNo(500, ret["code"], None, ret["message"])

        return ret["data"], None

    except Exception as e:
        print(f"fail to sign model: {str(e)}")
        return None, SIGN_FILE_ERR


def commit_file(signature: str, object_key: str) -> (dict, ErrorNo):
    server_url = f"{BIZYAIR_SERVER_ADDRESS}/x/v1/files"

    payload = {
        "sign": signature,
        "object_key": object_key,
    }
    headers, err = auth_header()
    if err is not None:
        return err

    try:
        resp = do_post(server_url, data=payload, headers=headers)
        ret = json.loads(resp)
        if ret["code"] != CODE_OK:
            return None, ErrorNo(500, ret["code"], None, ret["message"])

        return ret["data"], None
    except Exception as e:
        print(f"fail to commit file: {str(e)}")
        return None, COMMIT_FILE_ERR


def commit_model(
        model_files, model_name: str, model_type: str, overwrite: bool
) -> (dict, ErrorNo):
    server_url = f"{BIZYAIR_SERVER_ADDRESS}/x/v1/models"

    payload = {
        "name": model_name,
        "type": model_type,
        "overwrite": overwrite,
        "files": model_files,
    }
    headers, err = auth_header()
    if err is not None:
        return err

    try:
        resp = do_post(server_url, data=payload, headers=headers)
        ret = json.loads(resp)
        if ret["code"] != CODE_OK:
            return None, ErrorNo(500, ret["code"], None, ret["message"])

        return ret["data"], None
    except Exception as e:
        print(f"fail to commit model: {str(e)}")
        return None, COMMIT_MODEL_ERR


def remove_model(model_name: str, model_type: str) -> (dict, ErrorNo):
    server_url = f"{BIZYAIR_SERVER_ADDRESS}/x/v1/models"

    payload = {
        "name": model_name,
        "type": model_type,
    }
    headers, err = auth_header()
    if err is not None:
        return err

    try:
        resp = do_delete(server_url, data=payload, headers=headers)
        ret = json.loads(resp)
        if ret["code"] != CODE_OK:
            return ErrorNo(500, ret["code"], None, ret["message"])

        return None
    except Exception as e:
        print(f"fail to remove model: {str(e)}")
        return DELETE_MODEL_ERR


def is_string_valid(s):
    # 检查s是否已经被定义（即不是None）且不是空字符串
    if s is not None and s != "":
        return True
    else:
        return False


def to_slash(path):
    return path.replace("\\", "/")


def check_str_param(json_data, param_name: str, err):
    if param_name not in json_data:
        return ErrResponse(err)
    if not is_string_valid(json_data[param_name]):
        return ErrResponse(err)
    return None


def check_type(json_data):
    if "type" not in json_data:
        return ErrResponse(INVALID_TYPE)
    if not is_string_valid(json_data["type"]) or json_data["type"] not in ALLOW_TYPES:
        return ErrResponse(INVALID_TYPE)
    return None


def JsonResponse(http_status_code, data):
    return web.json_response(
        data, status=http_status_code, content_type="application/json"
    )


def OKResponse(data):
    return JsonResponse(200, {"message": "success", "code": CODE_OK, "data": data})


def ErrResponse(err: ErrorNo):
    return JsonResponse(
        err.http_status_code,
        {"message": err.message, "code": err.code, "data": err.data},
    )


def auth_header():
    try:
        api_key = bizyair.common.get_api_key()
        auth = f"Bearer {api_key}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
        return headers, None
    except ValueError as e:
        error_message = e.args[0] if e.args else INVALID_API_KEY.message
        INVALID_API_KEY.message = error_message
        return None, ErrResponse(INVALID_API_KEY)


def do_get(url, params=None, headers=None):
    # 将字典编码为URL参数字符串
    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"

    # 发送GET请求
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request) as response:
        return response.read().decode("utf-8")


def do_post(url, data=None, headers=None):
    # 将字典转换为字节串
    if data:
        data = bytes(json.dumps(data), "utf-8")

    # 创建请求对象
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")

    # 发送POST请求
    with urllib.request.urlopen(request) as response:
        return response.read().decode("utf-8")


def do_delete(url, data=None, headers=None):
    # 将字典转换为字节串
    if data:
        data = bytes(json.dumps(data), "utf-8")

    # 创建请求对象
    request = urllib.request.Request(url, data=data, headers=headers, method="DELETE")

    # 发送POST请求
    with urllib.request.urlopen(request) as response:
        return response.read().decode("utf-8")


def calculate_hash(file_path):
    # 读取文件并计算 CRC64
    # 创建CRC64校验函数。
    do_crc64 = crcmod.mkCrcFun(
        0x142F0E1EBA9EA3693, initCrc=0, xorOut=0xFFFFFFFFFFFFFFFF, rev=True
    )
    crc64_signature = 0
    buf_size = 65536  # 缓冲区大小为64KB

    # 打开文件并读取内容
    with open(file_path, "rb") as f:
        while chunk := f.read(buf_size):
            crc64_signature = do_crc64(chunk, crc64_signature)

    # 重新读取文件计算 MD5
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        while chunk := file.read(buf_size):
            md5_hash.update(chunk)
    md5_str = base64.b64encode(md5_hash.digest()).decode("utf-8")

    # 计算 SHA256
    hasher = hashlib.sha256()
    hasher.update(f"{md5_str}{crc64_signature}".encode("utf-8"))
    hash_string = hasher.hexdigest()

    # 调试信息输出
    logging.debug(
        f"file: {file_path}, crc64: {crc64_signature}, md5: {md5_str}, sha256: {hash_string}"
    )

    return hash_string
