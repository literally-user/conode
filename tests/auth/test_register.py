from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import RegisterRequestFactory, UserFactory


@pytest.mark.asyncio
async def test_register_ok(test_client: AsyncClient) -> None:
    response = await test_client.post(
        "/auth/register", json=RegisterRequestFactory.build().model_dump()
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        refresh_token=IsStr(),
        expires_in=IsInt(),
    )


@pytest.mark.asyncio
async def test_register_user_already_exists(
    test_client: AsyncClient, user_factory: UserFactory
) -> None:
    factory_result = await user_factory.create_user(admin=False)
    request = RegisterRequestFactory.build().model_dump()

    request.update({"email": factory_result.user.email.value})

    response = await test_client.post("/auth/register", json=request)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="User with this username or email already exists",
        meta=[
            {"key": "email", "value": request["email"]},
            {"key": "username", "value": request["username"]},
        ],
    )
