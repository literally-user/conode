from http import HTTPStatus

import pytest
from httpx import AsyncClient

from tests.factories import CompanyFactory, ContextFactory, UserFactory
from tests.services import EntityExistenceService


@pytest.mark.asyncio
async def test_delete_context_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    entity_existence_service: EntityExistenceService,
    context_factory: ContextFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    context = await context_factory.create_context(company)

    response = await test_client.delete(
        f"/contexts/{context.id}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert await entity_existence_service.exists(context) is False
