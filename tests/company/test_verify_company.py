from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories import CompanyFactory, UserFactory
from tests.services import EntityExistenceService


@pytest.mark.asyncio
async def test_verify_company_ok(
    company_factory: CompanyFactory,
    user_factory: UserFactory,
    test_client: AsyncClient,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=True)
    company_factory_response = await company_factory.create_company(
        user_factory_response.user
    )
    assert await entity_existence_service.exists(user_factory_response.user) is True
    assert await entity_existence_service.exists(company_factory_response) is True

    response = await test_client.patch(
        f"/companies/{company_factory_response.id}/verify",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_verify_company_not_enough_rights(
    company_factory: CompanyFactory,
    user_factory: UserFactory,
    test_client: AsyncClient,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company_factory_response = await company_factory.create_company(
        user_factory_response.user
    )
    assert await entity_existence_service.exists(user_factory_response.user) is True
    assert await entity_existence_service.exists(company_factory_response) is True

    response = await test_client.patch(
        f"/companies/{company_factory_response.id}/verify",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
