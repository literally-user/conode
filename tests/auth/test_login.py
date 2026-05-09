from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import UserFactory


@pytest.mark.asyncio
async def test_login_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
) -> None:
    factory_result = await user_factory.create_user(admin=False)

    response = await test_client.post(
        "/auth/login",
        json={
            "email": factory_result.user.email.value,
            "password": factory_result.password,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        refresh_token=IsStr(),
        expires_in=IsInt(),
    )


@pytest.mark.asyncio
async def test_login_invalid_credentials(
    test_client: AsyncClient,
    user_factory: UserFactory,
) -> None:
    factory_result = await user_factory.create_user(admin=False)

    response = await test_client.post(
        "/auth/login",
        json={
            "email": factory_result.user.email.value,
            "password": "TotallyInvalidPassword123456789",
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Invalid email or password",
        meta=[
            {"key": "email", "value": factory_result.user.email.value},
            {"key": "password", "value": "TotallyInvalidPassword123456789"},
        ],
    )
