from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import UserFactory, generate_random_string


@pytest.mark.asyncio
async def test_get_user_by_username_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
) -> None:
    users = [await user_factory.create_user(admin=False) for _ in range(2)]

    response = await test_client.get(
        f"/users/{users[0].user.username.value}",
        headers={"Authorization": f"Bearer {users[1].access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        id=IsStr(),
        first_name=users[0].user.first_name.value,
        last_name=users[0].user.last_name.value,
        username=users[0].user.username.value,
        email=users[0].user.email.value,
        bio=users[0].user.bio.value,
    )


@pytest.mark.asyncio
async def test_get_user_by_username_user_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    unknown_username = generate_random_string(10)

    response = await test_client.get(
        f"/users/{unknown_username}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="User not found",
        meta=[{"key": "username", "value": unknown_username}],
    )
