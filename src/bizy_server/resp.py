from aiohttp import web

from .errno import errnos, ErrorNo


def JsonResponse(http_status_code, data):
    return web.json_response(
        data,
        status=http_status_code,
        content_type="application/json",
    )


def OKResponse(data):
    return JsonResponse(200, {"message": "success", "code": errnos.OK.code, "data": data})


def ErrResponse(err: ErrorNo):
    return JsonResponse(
        err.http_status_code,
        {"message": err.message, "code": err.code, "data": err.data},
    )
