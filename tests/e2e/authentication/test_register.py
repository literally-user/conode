from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories.models import UserFactory
from tests.factories.schemas import RegisterRequestFactory


@pytest.mark.asyncio
async def test_register_ok(transport: AsyncClient) -> None:
    request = RegisterRequestFactory.build()

    response = await transport.post("/auth/register", json=request.model_dump())

    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_register_when_user_already_exists(
    transport: AsyncClient, user_factory: UserFactory
) -> None:
    user_factory_response = await user_factory.build()

    request = RegisterRequestFactory.build(
        email=user_factory_response.user.email.value,
        username=user_factory_response.user.username.value,
    )

    response = await transport.post("/auth/register", json=request.model_dump())

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="User with this username or email already exists",
        meta=[
            {"key": "email", "value": user_factory_response.user.email.value},
            {"key": "username", "value": user_factory_response.user.username.value},
        ],
    )
