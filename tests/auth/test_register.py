from http import HTTPStatus

import pytest
from dirty_equals import IsInt, IsPartialDict, IsStr
from httpx import AsyncClient

from prodik.application.interfaces.repositories import UserRepository
from prodik.domain.user import Email
from tests.factories import RegisterRequestFactory, UserFactory
from tests.services import EntityExistenceService


@pytest.mark.asyncio
async def test_register_ok(
    test_client: AsyncClient,
    user_repository: UserRepository,
    entity_existence_service: EntityExistenceService,
) -> None:
    request = RegisterRequestFactory.build().model_dump()
    response = await test_client.post("/auth/register", json=request)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        refresh_token=IsStr(),
        expires_in=IsInt(),
    )
    user = await user_repository.get_by_email(Email(request["email"]))
    assert user is not None
    assert await entity_existence_service.exists(user) is True


@pytest.mark.asyncio
async def test_register_user_already_exists(
    test_client: AsyncClient,
    user_factory: UserFactory,
    entity_existence_service: EntityExistenceService,
) -> None:
    factory_result = await user_factory.create_user(admin=False)
    assert await entity_existence_service.exists(factory_result.user) is True
    request = RegisterRequestFactory.build().model_dump()

    request.update({"email": factory_result.user.email.value})

    response = await test_client.post("/auth/register", json=request)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="User with this username or email already exists",
        meta=[
            {"key": "email", "value": request["email"]},
            {"key": "username", "value": request["username"]},
        ],
    )
