import argparse
import asyncio
import json

import aiohttp
from aiohttp import web


# Set up command-line argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description="OAuth Callback Server")
    parser.add_argument(
        "--account_endpoint",
        type=str,
        default="https://account.siliconflow.cn",
        help="The account endpoint URL",
    )
    parser.add_argument(
        "--cloud_endpoint",
        type=str,
        default="https://cloud.siliconflow.cn",
        help="The cloud endpoint URL",
    )
    parser.add_argument(
        "--client_id",
        type=str,
        default="SFaJLLq0y6CAMoyDm81aMu",
        help="The client ID for OAuth",
    )
    parser.add_argument(
        "--secret",
        type=str,
        required=True,
        help="The secret for OAuth",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="The port to run the server on",
    )

    return parser.parse_args()


args = parse_arguments()
ACCOUNT_ENDPOINT = args.account_endpoint
CLOUD_ENDPOINT = args.cloud_endpoint
client_id = args.client_id
secret = args.secret
port = args.port  # Added the port argument


async def fetch_api_key(request):
    code = request.rel_url.query.get("code")

    if not code:
        return web.Response(text="Missing 'code' parameter", status=400)

    token_fetch_url = f"{ACCOUNT_ENDPOINT}/api/open/oauth"

    # Prepare the payload
    payload = {"clientId": client_id, "secret": secret, "code": code}

    async with aiohttp.ClientSession() as session:
        # Make the first POST request to fetch the token
        async with session.post(token_fetch_url, json=payload) as response:
            if not response.ok:
                return web.Response(text="Failed to fetch access token", status=500)

            token_json = await response.json()
            access_token = (
                token_json["data"]["access_token"] if token_json.get("status") else None
            )

            if not access_token:
                return web.Response(text="Failed to retrieve access token", status=500)

            print("access_token", access_token)

            api_key_url = f"{CLOUD_ENDPOINT}/api/oauth/apikeys"
            headers = {"Authorization": f"token {access_token}"}

            # Make the second POST request to fetch API keys
            async with session.post(api_key_url, headers=headers) as api_key_response:
                api_keys_data = await api_key_response.json()
                print("apiKeysData", api_keys_data)

                if api_keys_data.get("data"):
                    return web.Response(
                        text=f"""
                        <html>
                        <head>
                            <title>BizyAir</title>
                        </head>
                        <body>
                            <h1>Just a moment...</h1>
                            <script>
                                window.opener.postMessage({json.dumps(api_keys_data["data"])}, '*');
                            </script>
                        </body>
                        </html>
                        """,
                        content_type="text/html",
                    )
                else:
                    return web.Response(text="Failed to fetch API key", status=500)


async def init_app():
    app = web.Application()
    app.router.add_get("/bizyair/oauth_callback", fetch_api_key)
    return app


if __name__ == "__main__":
    app = asyncio.run(init_app())
    web.run_app(app, port=port)  # Use the port argument here
