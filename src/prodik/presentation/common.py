from typing import Final

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from prodik.application.authorization.errors import (
    InvalidAccessHeaderError,
    InvalidClientError,
    InvalidCredentialsError,
    InvalidOldPasswordError,
    InvalidTokenError,
    UserAlreadyExistsError,
)
from prodik.application.errors import ApplicationError
from prodik.application.manage_company.errors import CompanyAlreadyExistsError
from prodik.domain.company.errors import CompanyDomainValidationError
from prodik.domain.context.errors import ContextDomainValidationError
from prodik.domain.contract.errors import ContractDomainValidationError
from prodik.domain.edge.errors import EdgeDomainValidationError
from prodik.domain.group.errors import GroupDomainValidationError
from prodik.domain.node.errors import NodeDomainValidationError
from prodik.domain.offer.errors import OfferDomainValidationError
from prodik.domain.role.errors import RoleDomainValidationError
from prodik.domain.user.errors import UserDomainValidationError
from prodik.presentation.auth import router as auth_router
from prodik.presentation.root import router as root_router

logger = structlog.get_logger(__name__)

DEFAULT_PREFIX: Final = "/api"
EXCEPTION_HANDLERS: Final[dict[type[ApplicationError], int]] = {
    UserDomainValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    CompanyDomainValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ContextDomainValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ContractDomainValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    EdgeDomainValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    GroupDomainValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    NodeDomainValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    OfferDomainValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    RoleDomainValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    UserAlreadyExistsError: status.HTTP_400_BAD_REQUEST,
    InvalidAccessHeaderError: status.HTTP_401_UNAUTHORIZED,
    InvalidClientError: status.HTTP_401_UNAUTHORIZED,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
    InvalidOldPasswordError: status.HTTP_401_UNAUTHORIZED,
    CompanyAlreadyExistsError: status.HTTP_409_CONFLICT,
}


async def application_error_handler(
    request: Request, exception: ApplicationError
) -> JSONResponse:
    status_code = EXCEPTION_HANDLERS.get(type(exception), status.HTTP_400_BAD_REQUEST)
    logger.warning(
        "Application error",
        path=request.url.path,
        method=request.method,
        status_code=status_code,
        error_type=type(exception).__name__,
        detail=exception.detail,
        meta=exception.meta,
    )
    return JSONResponse(
        status_code=status_code,
        content={"detail": exception.detail, "meta": exception.meta},
    )


async def unhandled_exception_handler(
    request: Request, exception: Exception
) -> JSONResponse:
    logger.exception(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error_type=type(exception).__name__,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def include_handlers(app: FastAPI) -> None:
    app.include_router(root_router, prefix=DEFAULT_PREFIX)
    app.include_router(auth_router, prefix=DEFAULT_PREFIX)


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)  # type: ignore
    app.add_exception_handler(Exception, unhandled_exception_handler)
