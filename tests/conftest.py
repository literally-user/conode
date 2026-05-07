from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from prodik.bootstrap.api import create_app
from prodik.infrastructure.config import Config, load_config


@pytest.fixture(scope="session")
def test_config() -> Config:
    return load_config("test.config.toml")


@pytest.fixture
async def test_client(test_config: Config) -> AsyncGenerator[AsyncClient]:
    app = create_app(test_config)

    async with AsyncClient(
        base_url="http://test.localhost.com", transport=ASGITransport(app)
    ) as client:
        yield client
