import json
import typing
from aiohttp.web import HTTPException, HTTPUnprocessableEntity, middleware, json_response
from aiohttp_apispec import validation_middleware
from aiohttp_session import get_session

from app.admin.models import AdminModel
from app.web.utils import error_json_response

if typing.TYPE_CHECKING:
    from app.web.app import Application, Request

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        return await handler(request)
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status="bad_request",
            message=e.reason,
            data=json.loads(e.text),
        )
    except HTTPException as e:
        return error_json_response(
            http_status=e.status,
            status=HTTP_ERROR_CODES.get(e.status, "unknown_error"),
            message=str(e.reason),
        )
    except Exception as e:
        request.app.logger.error("Exception", exc_info=e)
        return error_json_response(
            http_status=500,
            status="internal_server_error",
            message=str(e)
        )


@middleware
async def auth_middleware(request: "Request", handler):
    session = await get_session(request)
    admin_data = session.get("admin")
    if admin_data:
        request.admin = AdminModel(id=admin_data.get(
            "id"), email=admin_data.get("email"))
    else:
        request.admin = None
    return await handler(request)


def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(auth_middleware)
    app.middlewares.append(validation_middleware)
