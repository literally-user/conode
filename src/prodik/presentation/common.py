import time
from collections.abc import Awaitable, Callable
from typing import Final
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars

from prodik.application.errors import (
    ApplicationError,
    AuthorizationNotFoundError,
    FailedToReadClientError,
    InvalidCredentialsError,
    InvalidTokenError,
    SessionNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from prodik.presentation.auth import router as auth_router
from prodik.presentation.root import router as root_router
from prodik.presentation.user import router as user_router

logger = structlog.get_logger()

EXCEPTION_HANDLERS: Final[dict[type[ApplicationError], int]] = {
    UserAlreadyExistsError: status.HTTP_400_BAD_REQUEST,
    InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    SessionNotFoundError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationNotFoundError: status.HTTP_404_NOT_FOUND,
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    FailedToReadClientError: status.HTTP_400_BAD_REQUEST,
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
    logger.warning(
        "Handled application error",
        error_type=type(exception).__name__,
        detail=exception.detail,
        status_code=status_code,
        meta=exception.meta,
    )
    result = {"detail": exception.detail, "meta": exception.meta}
    return JSONResponse(status_code=status_code, content=result)


async def default_error_handler(
    _request: Request, exception: Exception
) -> JSONResponse:
    logger.exception(
        "Unhandled exception",
        error_type=type(exception).__name__,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


def include_handlers(app: FastAPI) -> None:
    app.include_router(root_router)
    app.include_router(auth_router)
    app.include_router(user_router)


def include_middlewares(app: FastAPI) -> None:
    app.add_middleware(LoggerMiddleware)


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)  # type: ignore
    app.add_exception_handler(Exception, default_error_handler)
