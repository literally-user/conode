from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import UserFactory


@pytest.mark.asyncio
async def test_get_current_user_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)

    response = await test_client.get(
        "/users/me/profile",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        id=IsStr(),
        first_name=user_factory_response.user.first_name.value,
        last_name=user_factory_response.user.last_name.value,
        username=user_factory_response.user.username.value,
        email=user_factory_response.user.email.value,
        bio=user_factory_response.user.bio.value,
    )
