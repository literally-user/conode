from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDataclass, IsPartialDict, IsStr
from httpx import AsyncClient

from prodik.application.interfaces.repositories import (
    LocalAuthorizationRepository,
    SessionRepository,
)
from prodik.application.interfaces.token_managers import AccessTokenManager
from tests.factories.models import UserFactory
from tests.factories.schemas import RegisterRequestFactory


@pytest.mark.asyncio
async def test_register_ok(
    transport: AsyncClient,
    session_repository: SessionRepository,
    access_token_manager: AccessTokenManager,
) -> None:
    request = RegisterRequestFactory.build()

    response = await transport.post("/auth/register", json=request.model_dump())
    content = response.json()

    session = await session_repository.get_by_token(content["refresh_token"])
    token_content = access_token_manager.decode(content["access_token"])

    assert response.status_code == HTTPStatus.CREATED

    assert session == IsPartialDataclass(
        user_id=token_content["user_id"],
        token=content["refresh_token"],
        host=IsStr,
    )
    assert content == IsPartialDict(
        access_token=IsStr,
        refresh_token=IsStr,
        expires_in=IsInt,
    )


@pytest.mark.asyncio
async def test_register_when_user_already_exists(
    transport: AsyncClient,
    user_factory: UserFactory,
    local_authorization_repository: LocalAuthorizationRepository,
) -> None:
    user_factory_response = await user_factory.build()

    request = RegisterRequestFactory.build(
        email=user_factory_response.user.email.value,
        username=user_factory_response.user.username.value,
    )

    response = await transport.post("/auth/register", json=request.model_dump())

    local_authorizations = await local_authorization_repository.get_all_by_user_id(
        user_factory_response.user.id
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert len(local_authorizations) == 1
    assert response.json() == IsPartialDict(
        detail="User with this username or email already exists",
        meta=[
            {"key": "email", "value": user_factory_response.user.email.value},
            {"key": "username", "value": user_factory_response.user.username.value},
        ],
    )
