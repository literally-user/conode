from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import UserFactory
from tests.services import EntityExistenceService


@pytest.mark.asyncio
async def test_refresh_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    entity_existence_service: EntityExistenceService,
) -> None:
    factory_result = await user_factory.create_user(admin=False)
    assert await entity_existence_service.exists(factory_result.user) is True

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
    entity_existence_service: EntityExistenceService,
) -> None:
    factory_result = await user_factory.create_user(admin=False)
    assert await entity_existence_service.exists(factory_result.user) is True

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
