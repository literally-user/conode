from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories.common import authorization_header, generate_random_string
from tests.factories.models import UserFactory
from tests.factories.schemas import RefreshTokenRequestFactory


@pytest.mark.asyncio
async def test_refresh_token_ok(
    transport: AsyncClient, user_factory: UserFactory
) -> None:
    user_factory_response = await user_factory.build()

    request = RefreshTokenRequestFactory.build(
        refresh_token=user_factory_response.refresh_token
    )

    response = await transport.post(
        "/auth/refresh",
        headers=authorization_header(user_factory_response.access_token),
        json=request.model_dump(),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        access_token=IsStr,
        refresh_token=IsStr,
        expires_in=IsInt,
    )


@pytest.mark.asyncio
async def test_refresh_token_without_active_session(
    transport: AsyncClient, user_factory: UserFactory
) -> None:
    user_factory_response = await user_factory.build()

    refresh_token = generate_random_string()
    request = RefreshTokenRequestFactory.build(refresh_token=refresh_token)

    response = await transport.post(
        "/auth/refresh",
        headers=authorization_header(user_factory_response.access_token),
        json=request.model_dump(),
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Session not found",
        meta=[{"key": "refresh_token", "value": refresh_token}],
    )
