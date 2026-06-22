from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_docs_availability(transport: AsyncClient) -> None:
    response = await transport.get("/docs")

    assert response.status_code == HTTPStatus.OK