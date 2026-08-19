from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDict, IsStr
from httpx import AsyncClient

from conode.application.interfaces.repositories import (
    AuthorizationRepository,
    SessionRepository,
    UserRepository,
)
from conode.domain.user import Email
from tests.factories.models import UserFactory
from tests.factories.schemas import RegisterRequestFactory


@pytest.mark.asyncio
async def test_register_ok(
    transport: AsyncClient,
    user_repository: UserRepository,
    authorization_repository: AuthorizationRepository,
    session_repository: SessionRepository,
) -> None:
    request = RegisterRequestFactory.build()

    response = await transport.post(
        "/auth/register", json=request.model_dump(mode="json")
    )
    content = response.json()

    user = await user_repository.get_by_email(Email(request.email))
    assert user is not None

    await authorization_repository.get_by_user(user)
    session = await session_repository.get_by_refresh_token(content["refresh_token"])

    assert response.status_code == HTTPStatus.CREATED
    assert content == IsPartialDict(
        access_token=IsStr(), refresh_token=session.refresh_token, expires_in=IsInt()
    )


@pytest.mark.asyncio
async def test_register_user_with_this_email_already_exists(
    transport: AsyncClient, user_factory: UserFactory
) -> None:
    user = await user_factory.build()

    request = RegisterRequestFactory.build(email=user.user.email.value)

    response = await transport.post(
        "/auth/register", json=request.model_dump(mode="json")
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="User with this username or email already exists",
        meta=[
            {"key": "email", "value": request.email},
            {"key": "username", "value": request.username},
        ],
    )


@pytest.mark.asyncio
async def test_register_user_with_this_username_already_exists(
    transport: AsyncClient, user_factory: UserFactory
) -> None:
    user = await user_factory.build()

    request = RegisterRequestFactory.build(username=user.user.username.value)

    response = await transport.post(
        "/auth/register", json=request.model_dump(mode="json")
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="User with this username or email already exists",
        meta=[
            {"key": "email", "value": request.email},
            {"key": "username", "value": request.username},
        ],
    )
