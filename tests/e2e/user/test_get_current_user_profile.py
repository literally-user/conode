from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories.common import authorization_headers
from tests.factories.models import UserFactory


@pytest.mark.asyncio
async def test_get_current_user_profile_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
) -> None:
    user = await user_factory.build()

    response = await transport.get(
        "/users/me/profile",
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
