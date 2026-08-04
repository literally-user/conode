from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDataclass, IsPartialDict
from httpx import AsyncClient

from conode.application.interfaces.repositories import UserRepository
from conode.domain.user import Bio, FirstName, LastName, Username
from tests.factories.common import authorization_headers
from tests.factories.models import UserFactory
from tests.factories.schemas import (
    UpdateUserProfileRequestFactory,
)


@pytest.mark.asyncio
async def test_update_foreign_user_profile_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    user_repository: UserRepository,
) -> None:
    users = (await user_factory.build(admin=True), await user_factory.build())

    request = UpdateUserProfileRequestFactory.build()

    response = await transport.put(
        f"/users/me/profile/{users[1].user.id}",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(users[0].access_token),
    )
    result = await user_repository.get_by_id(users[1].user.id)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert result == IsPartialDataclass(
        first_name=FirstName(request.first_name),
        last_name=LastName(request.last_name),
        username=Username(request.username),
        bio=Bio(request.bio),
    )


@pytest.mark.asyncio
async def test_update_self_user_profile_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    user_repository: UserRepository,
) -> None:
    user = await user_factory.build()

    request = UpdateUserProfileRequestFactory.build()

    response = await transport.put(
        f"/users/me/profile/{user.user.id}",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(user.access_token),
    )
    result = await user_repository.get_by_id(user.user.id)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert result == IsPartialDataclass(
        first_name=FirstName(request.first_name),
        last_name=LastName(request.last_name),
        username=Username(request.username),
        bio=Bio(request.bio),
    )


@pytest.mark.asyncio
async def test_update_foreign_user_profile_without_correct_rights(
    transport: AsyncClient,
    user_factory: UserFactory,
    user_repository: UserRepository,
) -> None:
    users = (await user_factory.build(), await user_factory.build())

    request = UpdateUserProfileRequestFactory.build()

    response = await transport.put(
        f"/users/me/profile/{users[1].user.id}",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(users[0].access_token),
    )
    result = await user_repository.get_by_id(users[1].user.id)

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation", meta=None
    )
    assert result == IsPartialDataclass(
        first_name=users[1].user.first_name,
        last_name=users[1].user.last_name,
        username=users[1].user.username,
        bio=users[1].user.bio,
    )
