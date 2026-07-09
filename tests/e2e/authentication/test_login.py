from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDataclass, IsPartialDict, IsStr
from httpx import AsyncClient

from prodik.application.interfaces.repositories import SessionRepository
from tests.factories.models import UserFactory
from tests.factories.schemas import LoginRequestFactory


@pytest.mark.asyncio
async def test_login_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    session_repository: SessionRepository,
) -> None:
    user_factory_response = await user_factory.build()

    request = LoginRequestFactory.build(
        email=user_factory_response.user.email.value,
        password=user_factory_response.password,
    )

    response = await transport.post("/auth/login", json=request.model_dump())
    content = response.json()

    session = await session_repository.get_by_host_and_user_id(
        user_factory_response.user.id, "127.0.0.1"
    )

    assert response.status_code == HTTPStatus.OK
    assert session == IsPartialDataclass(
        user_id=str(user_factory_response.user.id),
        token=content["refresh_token"],
        host="127.0.0.1",
    )
    assert content == IsPartialDict(
        access_token=IsStr,
        refresh_token=IsStr,
        expires_in=IsInt,
    )


@pytest.mark.asyncio
async def test_login_invalid_password(
    transport: AsyncClient,
    user_factory: UserFactory,
    session_repository: SessionRepository,
) -> None:
    user_factory_response = await user_factory.build()

    request = LoginRequestFactory.build(
        email=user_factory_response.user.email.value,
        password="",
    )

    response = await transport.post("/auth/login", json=request.model_dump())

    session = await session_repository.get_by_token(user_factory_response.refresh_token)

    assert session is not None
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Invalid email or password",
        meta=[
            {"key": "email", "value": request.email},
            {"key": "password", "value": request.password},
        ],
    )
