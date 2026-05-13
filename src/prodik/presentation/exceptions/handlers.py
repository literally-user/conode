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
    GrantAlreadyExistsError,
    GrantNotFoundError,
    GroupNotFoundError,
    InvalidCredentialsError,
    InvalidOldPasswordError,
    InvalidTokenError,
    NodeCannotHaveSameAssociationsError,
    NodeMustHaveAtLeastOneAssociationError,
    NodeNotFoundError,
    NotEnoughRightsError,
    RoleAlreadyExistsError,
    RoleNotFoundError,
    SessionNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from prodik.domain.company.errors import CompanyDomainValidationError
from prodik.domain.context.errors import ContextDomainValidationError
from prodik.domain.edge.errors import EdgeDomainValidationError
from prodik.domain.group.errors import GroupDomainValidationError
from prodik.domain.node.errors import NodeDomainValidationError
from prodik.domain.role.errors import RoleDomainValidationError
from prodik.domain.user.errors import UserDomainValidationError

logger = structlog.get_logger()

EXCEPTION_HANDLERS: Final[dict[type[ApplicationError], HTTPStatus]] = {
    UserAlreadyExistsError: HTTPStatus.CONFLICT,
    CompanyAlreadyExistsError: HTTPStatus.CONFLICT,
    EdgeAlreadyExistsError: HTTPStatus.CONFLICT,
    InvalidTokenError: HTTPStatus.UNAUTHORIZED,
    InvalidCredentialsError: HTTPStatus.UNAUTHORIZED,
    RoleAlreadyExistsError: HTTPStatus.CONFLICT,
    RoleNotFoundError: HTTPStatus.NOT_FOUND,
    SessionNotFoundError: HTTPStatus.UNAUTHORIZED,
    AuthorizationNotFoundError: HTTPStatus.NOT_FOUND,
    GrantAlreadyExistsError: HTTPStatus.CONFLICT,
    GrantNotFoundError: HTTPStatus.NOT_FOUND,
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
    NodeCannotHaveSameAssociationsError: HTTPStatus.CONFLICT,
    NodeMustHaveAtLeastOneAssociationError: HTTPStatus.CONFLICT,
    CompanyDomainValidationError: HTTPStatus.UNPROCESSABLE_CONTENT,
    ContextDomainValidationError: HTTPStatus.UNPROCESSABLE_CONTENT,
    EdgeDomainValidationError: HTTPStatus.UNPROCESSABLE_CONTENT,
    GroupDomainValidationError: HTTPStatus.UNPROCESSABLE_CONTENT,
    NodeDomainValidationError: HTTPStatus.UNPROCESSABLE_CONTENT,
    RoleDomainValidationError: HTTPStatus.UNPROCESSABLE_CONTENT,
    UserDomainValidationError: HTTPStatus.UNPROCESSABLE_CONTENT,
}


async def application_error_handler(
    _request: Request, exception: ApplicationError
) -> JSONResponse:
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    for error in type(exception).mro():
        if error in EXCEPTION_HANDLERS:
            status_code = EXCEPTION_HANDLERS[error]

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
