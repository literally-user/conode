from http import HTTPStatus

import pytest
from httpx import AsyncClient

from tests.factories.common import authorization_headers
from tests.factories.models import UserFactory


@pytest.mark.asyncio
async def test_update_verified_flag_after_request_ok(
    transport: AsyncClient, user_factory: UserFactory
) -> None:
    user = await user_factory.build()

    response = await transport.get(
        "users/me/profile", headers=authorization_headers(user.access_token)
    )
    assert response.status_code == HTTPStatus.OK
    assert not response.json()["email_verified"]

    user.user.email_verified = True
    user.access_token = user_factory.generate_access_token(user.user)

    response = await transport.get(
        "users/me/profile", headers=authorization_headers(user.access_token)
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["email_verified"]
