from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from conode.bootstrap.di import get_async_container
from conode.bootstrap.logs import configure_structlog
from conode.bootstrap.telemetry import configure_telemetry
from conode.infrastructure.config import Config, load_config
from conode.presentation.common import (
    include_exception_handlers,
    include_handlers,
    include_middlewares,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await app.state.dishka_container.close()


def create_app(config: Config) -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        docs_url="/docs" if config.api.debug else None,
        redoc_url="/redoc" if config.api.debug else None,
        openapi_url="/openapi.json" if config.api.debug else None,
        title="application",
        description="Great & powerful application",
        version="0.1.0",
    )

    include_handlers(app)
    include_middlewares(app)
    include_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def run_http(_argv: list[str]) -> None:
    config = load_config()

    app = create_app(config)

    configure_telemetry(config.otel)

    container = get_async_container(config)
    log_configuration = configure_structlog()

    FastAPIInstrumentor().instrument_app(app)

    setup_dishka(app=app, container=container)

    uvicorn.run(
        app=app,
        host=config.api.host,
        port=config.api.port,
        log_config=log_configuration,
    )
