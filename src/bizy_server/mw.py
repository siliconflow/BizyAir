from aiohttp import web


# 自定义错误响应
async def error_middleware(app, handler):
    async def middleware_handler(request):
        try:
            response = await handler(request)
            return response
        except web.HTTPRequestEntityTooLarge:
            return web.json_response(
                {"error": "File size exceeds the allowed limit. Please use the \"--client_max_size\" option to "
                          "specify the upload file size limit, default is 10MB."}, status=413
            )
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    return middleware_handler
