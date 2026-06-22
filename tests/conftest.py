from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport

from prodik.bootstrap.api.run import create_app
from prodik.infrastructure.config import Config, load_config

@pytest.fixture(scope="session")
def config() -> Config:
    return load_config("test.config.toml")

@pytest.fixture
async def transport(config: Config) -> AsyncClient:
    app = create_app(config)

    return AsyncClient(
        base_url="http://test.environment.org",
        transport=ASGITransport(app)
    )