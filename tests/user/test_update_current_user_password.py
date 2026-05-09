from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import UserFactory


@pytest.mark.asyncio
async def test_update_current_user_password_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
) -> None:
    factory_result = await user_factory.create_user(admin=False)

    response = await test_client.put(
        "/users/me/password",
        json={
            "old_password": factory_result.password,
            "new_password": "NewSuperSecretPassword123456",
        },
        headers={"Authorization": f"Bearer {factory_result.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        refresh_token=IsStr(),
        expires_in=IsInt(),
    )


@pytest.mark.asyncio
async def test_update_current_user_password_invalid_old_password(
    test_client: AsyncClient,
    user_factory: UserFactory,
) -> None:
    factory_result = await user_factory.create_user(admin=False)

    response = await test_client.put(
        "/users/me/password",
        json={
            "old_password": "TOTALYINVALIDPASSWORD12348904567890",
            "new_password": "NewSuperSecretPassword123456",
        },
        headers={"Authorization": f"Bearer {factory_result.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Invalid old password",
        meta=[
            {"key": "old_password", "value": "TOTALYINVALIDPASSWORD12348904567890"},
        ],
    )
