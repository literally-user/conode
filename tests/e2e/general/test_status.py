from http import HTTPStatus

from dirty_equals import IsPartialDict
from httpx import AsyncClient


async def test_api_status(transport: AsyncClient) -> None:
    response = await transport.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(status=HTTPStatus.OK)
