from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ping(test_client: AsyncClient) -> None:
    result = await test_client.get("/")

    assert result.status_code == HTTPStatus.OK
