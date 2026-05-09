from http import HTTPStatus
from uuid import UUID

import pytest
from dirty_equals import IsPartialDict, IsStr, IsUUID
from httpx import AsyncClient

from prodik.application.interfaces.repositories import ContextRepository
from prodik.domain.context import ContextId
from tests.factories import CompanyFactory, UserFactory
from tests.services import EntityExistenceService


@pytest.mark.asyncio
async def test_create_context_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_repository: ContextRepository,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)

    response = await test_client.post(
        "/contexts/",
        json={
            "name": "test-context",
            "description": "context for tests",
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        id=IsUUID(),
        name="test-context",
        description="context for tests",
        company_id=str(company.id),
        created_at=IsStr(),
        updated_at=IsStr(),
    )

    context = await context_repository.get_by_id(ContextId(UUID(response.json()["id"])))
    assert await entity_existence_service.exists(context) is True


@pytest.mark.asyncio
async def test_create_context_company_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)

    response = await test_client.post(
        "/contexts/",
        json={
            "name": "test-context",
            "description": "context for tests",
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Company not found", meta=None)
