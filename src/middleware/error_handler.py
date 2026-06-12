import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def _error_json(error_type: str, message: str, status_code: int) -> dict:
    return {"error": error_type, "message": message, "statusCode": status_code}


def setup_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        error_type = "http_error"
        message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)

        if exc.status_code == 404:
            error_type = "not_found"
            message = f"The requested resource '{request.url.path}' was not found."
        elif exc.status_code == 405:
            error_type = "method_not_allowed"
            message = f"Method {request.method} not allowed for {request.url.path}"

        return JSONResponse(
            status_code=exc.status_code,
            content=_error_json(error_type, message, exc.status_code),
        )

    # Integer handlers — required for Starlette Router-level unmatched routes (404)
    # and method-not-allowed (405), which look up handlers by status code integer.
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=404,
            content=_error_json(
                "not_found",
                f"The requested resource '{request.url.path}' was not found.",
                404,
            ),
        )

    @app.exception_handler(405)
    async def method_not_allowed_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=405,
            content=_error_json(
                "method_not_allowed",
                f"Method {request.method} not allowed for {request.url.path}",
                405,
            ),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content=_error_json(
                "internal_error",
                "An unexpected error occurred. Please try again later.",
                500,
            ),
        )
