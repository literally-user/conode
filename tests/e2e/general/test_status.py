from http import HTTPStatus

from httpx import AsyncClient
from dirty_equals import IsPartialDict


async def test_api_status(transport: AsyncClient) -> None:
    response = await transport.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        status=HTTPStatus.OK
    )