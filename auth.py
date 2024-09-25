import os
import uuid
from pathlib import Path

import requests
import server
from aiohttp import web

import bizyair
from bizyair.common import create_api_key_file, load_api_key, validate_api_key

API_KEY = None
html_file_path = Path(os.path.dirname(os.path.abspath(__file__))) / "set_api_key.html"
with open(html_file_path, "r", encoding="utf-8") as htmlfile:
    set_api_key_html = htmlfile.read()


has_key, api_key = load_api_key()
if has_key:
    API_KEY = api_key


@server.PromptServer.instance.routes.get("/bizyair/set-api-key")
async def set_api_key_page(request):
    return web.Response(text=set_api_key_html, content_type="text/html")


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
            bizyair.set_api_key(API_KEY, override=True)
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
            bizyair.set_api_key(API_KEY)
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
            bizyair.set_api_key(API_KEY)
            return web.Response(text="Key has been loaded from the cookies")

    except Exception as e:
        return web.Response(text=str(e), status=500)


@server.PromptServer.instance.routes.get("/bizyair/oauth_callback")
async def fetch_api_key(request):
    ACCOUNT_ENDPOINT = "https://account.siliconflow.cn"
    CLOUD_ENDPOINT = "https://cloud.siliconflow.cn"
    client_id = "SFaJLLq0y6CAMoyDm81aMu"
    secret = "wcc4pJXTL9oD9Ub1SpeZNtfFlMwRkYdWKlDnz3gK"

    code = request.rel_url.query["code"]

    token_fetch_url = f"{ACCOUNT_ENDPOINT}/api/open/oauth"

    # Prepare the payload
    payload = {"clientId": client_id, "secret": secret, "code": code}

    # Make the first POST request to fetch the token
    response = requests.post(token_fetch_url, json=payload)

    if not response.ok:
        return web.Response(text="fail to fetch access token", status=500)

    token_json = response.json()
    access_token = (
        token_json["data"]["access_token"] if token_json.get("status") else None
    )
    print("access_token", access_token)

    api_key_url = f"{CLOUD_ENDPOINT}/api/oauth/apikeys"
    headers = {"Authorization": f"token {access_token}"}

    # Make the second POST request to fetch API keys
    api_key_response = requests.post(api_key_url, headers=headers)
    api_keys_data = api_key_response.json()
    print("apiKeysData", api_keys_data)

    return (
        # web.json_response({"api_key": api_keys_data["data"][0]["secretKey"]})
        web.Response(
            text=f"""
<html>
<head>
    <title>New Window</title>
</head>
<body>
    <h1>Just a moment...</h1>
    <script>
        window.opener.postMessage("{api_keys_data["data"][0]["secretKey"]}", window.location.origin);
    </script>
</body>
</html>
""",
            content_type="text/html",
        )
        if api_keys_data.get("data")
        else web.Response(text="fail to fetch API key", status=500)
    )


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
