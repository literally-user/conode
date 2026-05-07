import time
from collections.abc import Awaitable, Callable
from typing import Final
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars

from prodik.application.errors import ApplicationError, UserAlreadyExistsError
from prodik.presentation.auth import router as auth_router
from prodik.presentation.root import router as root_router

logger = structlog.get_logger()

EXCEPTION_HANDLERS: Final[dict[type[ApplicationError], int]] = {
    UserAlreadyExistsError: status.HTTP_400_BAD_REQUEST
}


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        bind_contextvars(request_id=str(uuid4()))

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        logger.debug(
            "Processed request",
            method=request.method,
            url=request.url.path,
            time=process_time,
        )

        return response


async def application_error_handler(
    _request: Request, exception: ApplicationError
) -> JSONResponse:
    status_code = EXCEPTION_HANDLERS.get(
        type(exception), status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    result = {"detail": exception.detail, "meta": exception.meta}
    return JSONResponse(status_code=status_code, content=result)


def include_handlers(app: FastAPI) -> None:
    app.include_router(root_router)
    app.include_router(auth_router)


def include_middlewares(app: FastAPI) -> None:
    app.add_middleware(LoggerMiddleware)


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)  # type: ignore
