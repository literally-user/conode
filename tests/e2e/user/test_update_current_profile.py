from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDataclass
from httpx import AsyncClient

from prodik.application.interfaces.repositories import UserRepository
from prodik.domain.user import Bio, Email, FirstName, LastName, Username
from tests.factories.common import authorization_headers
from tests.factories.models import UserFactory
from tests.factories.schemas import (
    UpdateCurrentUserProfileRequestFactory,
)


@pytest.mark.asyncio
async def test_update_current_user_profile_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    user_repository: UserRepository,
) -> None:
    user = await user_factory.build()

    request = UpdateCurrentUserProfileRequestFactory.build()

    response = await transport.put(
        "/users/me/profile",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(user.access_token),
    )
    result = await user_repository.get_by_id(user.user.id)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert result == IsPartialDataclass(
        first_name=FirstName(request.first_name),
        last_name=LastName(request.last_name),
        username=Username(request.username),
        email=Email(request.email),
        bio=Bio(request.bio),
    )
