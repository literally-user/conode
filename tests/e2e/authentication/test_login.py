from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories.models import UserFactory
from tests.factories.schemas import LoginRequestFactory


@pytest.mark.asyncio
async def test_login_ok(transport: AsyncClient, user_factory: UserFactory) -> None:
    user_factory_response = await user_factory.build()

    request = LoginRequestFactory.build(
        email=user_factory_response.user.email.value,
        password=user_factory_response.password,
    )

    response = await transport.post("/auth/login", json=request.model_dump())

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        access_token=IsStr,
        refresh_token=IsStr,
        expires_in=IsInt,
    )


@pytest.mark.asyncio
async def test_login_invalid_password(
    transport: AsyncClient, user_factory: UserFactory
) -> None:
    user_factory_response = await user_factory.build()

    request = LoginRequestFactory.build(
        email=user_factory_response.user.email.value,
        password="",
    )

    response = await transport.post("/auth/login", json=request.model_dump())

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Invalid email or password",
        meta=[
            {"key": "email", "value": request.email},
            {"key": "password", "value": request.password},
        ],
    )
