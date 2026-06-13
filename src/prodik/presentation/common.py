import structlog
from fastapi import FastAPI

from prodik.application.errors import ApplicationError
from prodik.presentation.exceptions import (
    application_error_handler,
    default_error_handler,
)
from prodik.presentation.middlewares import LoggerMiddleware
from prodik.presentation.views import (
    auth,
    company,
    context,
    edge,
    group,
    node,
    offer,
    role,
    root,
    user,
)

logger = structlog.get_logger()


def include_handlers(app: FastAPI) -> None:
    app.include_router(company)
    app.include_router(context)
    app.include_router(group)
    app.include_router(offer)
    app.include_router(role)
    app.include_router(root)
    app.include_router(auth)
    app.include_router(user)
    app.include_router(node)
    app.include_router(edge)


def include_middlewares(app: FastAPI) -> None:
    app.add_middleware(LoggerMiddleware)


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)  # type: ignore
    app.add_exception_handler(Exception, default_error_handler)
