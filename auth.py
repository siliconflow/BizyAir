import uuid
import os
import configparser
import server
from aiohttp import web
import bizyair


API_KEY = None
set_api_key_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BizyAir - Set API Key</title>
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
        }
        input[type="password"] {
            padding: 10px;
            margin: 10px;
            border: 2px solid rgb(130, 88, 245);
            border-radius: 5px;
            background-color: #1e1e1e;
            color: #ffffff;
            width: 200px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: rgb(130, 88, 245);
            color: #ffffff;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
    <script>
        async function setApiKey() {
            const apiKey = document.getElementById('apiKey').value;
            let endpoint = location.href;
            if(endpoint.includes('/bizyair/set-api-key'))
               endpoint = endpoint.replace('/bizyair/set-api-key','/bizyair/set_api_key');
            else
               endpoint =`${endpoint}/bizyair/set_api_key`;
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `api_key=${encodeURIComponent(apiKey)}`
            });
            if (response.ok) {
                alert('API Key set successfully!');
                if (window.opener) {
                    window.close();
                }
            } else {
                alert('Failed to set API Key: ' + await response.text());
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Set API Key</h1>
        <input type="password" id="apiKey" placeholder="Enter API Key">
        <button onclick="setApiKey()">Set API Key</button>
        <p>To get your key, visit <a href="https://cloud.siliconflow.cn" target="_blank">https://cloud.siliconflow.cn</a></p>
    </div>
</body>
</html>
    </div>
</body>
</html>
"""


def load_api_key():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, "api_key.ini")

    if os.path.exists(file_path):
        config = configparser.ConfigParser()
        config.read(file_path)
        api_key: str = config.get("auth", "api_key", fallback="").strip().strip("'\"")
        has_key = api_key.startswith("sk-")
        return has_key, api_key
    else:
        return False, ""


has_key, api_key = load_api_key()
if has_key:
    API_KEY = api_key


@server.PromptServer.instance.routes.get("/bizyair/set-api-key")
async def set_api_key_page(request):
    return web.Response(text=set_api_key_html, content_type="text/html")


@server.PromptServer.instance.routes.post("/bizyair/set_api_key")
async def set_api_key(request):
    global API_KEY
    has_key, api_key = load_api_key()
    if has_key:
        API_KEY = api_key
        bizyair.set_api_key(API_KEY)
        return web.Response(text="Key has been loaded from the api_key.ini file")
    data = await request.post()
    api_key = data.get("api_key")
    try:
        if api_key:
            response = web.Response(text="ok")
            response.set_cookie("api_key", api_key, max_age=30 * 24 * 60 * 60)
            API_KEY = api_key
            bizyair.set_api_key(API_KEY)
            return response
        else:
            return web.Response(
                text="No token provided, please refer to cloud.siliconflow.cn to get the key",
                status=400,
            )
    except Exception as e:
        return web.Response(text=str(e), status=500)


@server.PromptServer.instance.routes.get("/bizyair/get_api_key")
async def get_api_key(request):
    global API_KEY
    has_key, api_key = load_api_key()
    if has_key:
        API_KEY = api_key
        bizyair.set_api_key(API_KEY)
        return web.Response(text="Key has been loaded from the api_key.ini file")

    if api_key == "":
        api_key = request.cookies.get("api_key")
    try:
        if api_key:
            API_KEY = api_key
            response = web.Response(text="ok")
            bizyair.set_api_key(API_KEY)
            return response
        else:
            return web.Response(
                text="No api key found in cookie, please refer to cloud.siliconflow.cn to get the key",
                status=404,
            )
    except Exception as e:
        return web.Response(text="str(e)", status=500)
