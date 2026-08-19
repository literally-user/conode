from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDict, IsStr
from httpx import AsyncClient

from conode.application.interfaces.repositories import SessionRepository
from tests.factories.models import UserFactory
from tests.factories.schemas import RefreshTokenRequestFactory


@pytest.mark.asyncio
async def test_refresh_token_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    session_repository: SessionRepository,
) -> None:
    user = await user_factory.build()

    request = RefreshTokenRequestFactory.build(refresh_token=user.refresh_token)

    session = await session_repository.get_by_ip_and_user(user.user, "127.0.0.1")
    old_refresh_token = session.refresh_token  # type: ignore

    response = await transport.post(
        "/auth/refresh",
        json=request.model_dump(mode="json"),
    )
    content = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        access_token=IsStr(), refresh_token=IsStr(), expires_in=IsInt()
    )
    assert content["refresh_token"] != old_refresh_token


@pytest.mark.asyncio
async def test_refresh_token_with_invalid_token(
    transport: AsyncClient,
) -> None:
    request = RefreshTokenRequestFactory.build(refresh_token="invalid_token")  # noqa: S106

    response = await transport.post(
        "/auth/refresh", json=request.model_dump(mode="json")
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Session associated with this refresh token not found",
        meta=[{"key": "token", "value": request.refresh_token}],
    )
