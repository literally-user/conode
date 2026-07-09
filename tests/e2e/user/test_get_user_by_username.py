from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories.common import authorization_headers, generate_random_string
from tests.factories.models import UserFactory


@pytest.mark.asyncio
async def test_get_user_by_username_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
) -> None:
    user = await user_factory.build()

    response = await transport.get(
        f"/users/{user.user.username.value}",
        headers=authorization_headers(user.access_token),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        id=str(user.user.id),
        username=user.user.username,
        first_name=user.user.first_name,
        last_name=user.user.last_name,
        email=user.user.email,
        bio=user.user.bio,
    )


@pytest.mark.asyncio
async def test_get_user_by_username_not_found(
    transport: AsyncClient,
    user_factory: UserFactory,
) -> None:
    user = await user_factory.build()

    username = generate_random_string()
    response = await transport.get(
        f"/users/{username}",
        headers=authorization_headers(user.access_token),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="User not found", meta=[{"key": "username", "value": username}]
    )
