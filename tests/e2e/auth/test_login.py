from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDict, IsStr
from httpx import AsyncClient

from conode.application.interfaces.repositories import (
    SessionRepository,
)
from tests.factories.models import UserFactory
from tests.factories.schemas import LoginRequestFactory


@pytest.mark.asyncio
async def test_login_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    session_repository: SessionRepository,
) -> None:
    user = await user_factory.build()

    request = LoginRequestFactory.build(
        email=user.user.email.value, password=user.password
    )

    response = await transport.post("/auth/login", json=request.model_dump(mode="json"))

    session = await session_repository.get_by_ip_and_user(user.user, "127.0.0.1")

    assert session is not None
    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        access_token=IsStr(), refresh_token=session.refresh_token, expires_in=IsInt()
    )


@pytest.mark.asyncio
async def test_login_invalid_password(
    transport: AsyncClient,
    user_factory: UserFactory,
) -> None:
    user = await user_factory.build()

    request = LoginRequestFactory.build(email=user.user.email.value)

    response = await transport.post("/auth/login", json=request.model_dump(mode="json"))

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Passwords doesn't match",
        meta=[{"key": "password", "value": request.password}],
    )
