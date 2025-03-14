from aiohttp import web

from .errno import ErrorNo, errnos
from .profile import user_profile


def JsonResponse(http_status_code, data):
    return web.json_response(
        data,
        status=http_status_code,
        content_type="application/json",
    )


def OKResponse(data):
    message = "成功" if user_profile.getLang() == "zh" else "success"
    return JsonResponse(200, {"message": message, "code": errnos.OK.code, "data": data})


def ErrResponse(err: ErrorNo):
    err_msg = err.messages.get(user_profile.getLang())
    if not err_msg:
        err.messages["zh"]

    return JsonResponse(
        err.http_status_code,
        {"message": err_msg, "code": err.code, "data": err.data},
    )
