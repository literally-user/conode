import structlog
from fastapi import FastAPI

from prodik.application.errors import ApplicationError
from prodik.presentation.auth import router as auth_router
from prodik.presentation.company import router as company_router
from prodik.presentation.context import router as context_router
from prodik.presentation.edge import router as edge_router
from prodik.presentation.exceptions import (
    application_error_handler,
    default_error_handler,
)
from prodik.presentation.group import router as group_router
from prodik.presentation.middlewares import LoggerMiddleware
from prodik.presentation.node import router as node_router
from prodik.presentation.root import router as root_router
from prodik.presentation.user import router as user_router

logger = structlog.get_logger()


def include_handlers(app: FastAPI) -> None:
    app.include_router(company_router)
    app.include_router(group_router)
    app.include_router(root_router)
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(node_router)
    app.include_router(edge_router)
    app.include_router(context_router)


def include_middlewares(app: FastAPI) -> None:
    app.add_middleware(LoggerMiddleware)


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)  # type: ignore
    app.add_exception_handler(Exception, default_error_handler)
