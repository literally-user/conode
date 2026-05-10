from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import UserFactory


@pytest.mark.asyncio
async def test_refresh_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
) -> None:
    factory_result = await user_factory.create_user(admin=False)

    response = await test_client.post(
        "/auth/refresh",
        json={"refresh_token": factory_result.refresh_token},
        headers={"Authorization": f"Bearer {factory_result.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        refresh_token=IsStr(),
        expires_in=IsInt(),
    )


@pytest.mark.asyncio
async def test_refresh_session_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
) -> None:
    factory_result = await user_factory.create_user(admin=False)

    response = await test_client.post(
        "/auth/refresh",
        json={"refresh_token": "totally-invalid-refresh-token"},
        headers={"Authorization": f"Bearer {factory_result.access_token}"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Session not found",
        meta=None,
    )


@pytest.mark.asyncio
async def test_refresh_invalid_access_token(
    test_client: AsyncClient,
    user_factory: UserFactory,
) -> None:
    factory_result = await user_factory.create_user(admin=False)

    response = await test_client.post(
        "/auth/refresh",
        json={"refresh_token": factory_result.refresh_token},
        headers={"Authorization": "Bearer totally-invalid-access-token"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Invalid authorization token",
    )
