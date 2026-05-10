from http import HTTPStatus
from typing import Final

import structlog
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from prodik.application.errors import (
    ApplicationError,
    AssociationNotFoundError,
    AuthorizationNotFoundError,
    CompanyAlreadyExistsError,
    CompanyNotFoundError,
    ContextNotFoundError,
    EdgeAlreadyExistsError,
    EdgeNotFoundError,
    FailedToReadClientError,
    GroupNotFoundError,
    InvalidCredentialsError,
    InvalidOldPasswordError,
    InvalidTokenError,
    NodeNotFoundError,
    NotEnoughRightsError,
    SessionNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

logger = structlog.get_logger()

EXCEPTION_HANDLERS: Final[dict[type[ApplicationError], HTTPStatus]] = {
    UserAlreadyExistsError: HTTPStatus.CONFLICT,
    CompanyAlreadyExistsError: HTTPStatus.CONFLICT,
    EdgeAlreadyExistsError: HTTPStatus.CONFLICT,
    InvalidTokenError: HTTPStatus.UNAUTHORIZED,
    InvalidCredentialsError: HTTPStatus.UNAUTHORIZED,
    SessionNotFoundError: HTTPStatus.UNAUTHORIZED,
    AuthorizationNotFoundError: HTTPStatus.NOT_FOUND,
    UserNotFoundError: HTTPStatus.NOT_FOUND,
    CompanyNotFoundError: HTTPStatus.NOT_FOUND,
    ContextNotFoundError: HTTPStatus.NOT_FOUND,
    EdgeNotFoundError: HTTPStatus.NOT_FOUND,
    NodeNotFoundError: HTTPStatus.NOT_FOUND,
    GroupNotFoundError: HTTPStatus.NOT_FOUND,
    AssociationNotFoundError: HTTPStatus.NOT_FOUND,
    FailedToReadClientError: HTTPStatus.BAD_REQUEST,
    InvalidOldPasswordError: HTTPStatus.FORBIDDEN,
    NotEnoughRightsError: HTTPStatus.FORBIDDEN,
}


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
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"detail": exception.detail, "meta": exception.meta}),
    )


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
