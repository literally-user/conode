from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from prodik.application.interfaces.repositories import CompanyRepository
from tests.factories import CompanyFactory, RegisterCompanyRequestFactory, UserFactory
from tests.services import EntityExistenceService


@pytest.mark.asyncio
async def test_register_company_ok(
    user_factory: UserFactory,
    test_client: AsyncClient,
    company_repository: CompanyRepository,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    assert await entity_existence_service.exists(user_factory_response.user) is True
    request_factory_response = RegisterCompanyRequestFactory.build().model_dump()

    response = await test_client.post(
        "/companies/",
        json=request_factory_response,
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        name=request_factory_response["name"],
        owner_id=str(user_factory_response.user.id),
        description=request_factory_response["description"],
        verified=False,
    )
    company = await company_repository.get_by_user_id(user_factory_response.user.id)
    assert company is not None
    assert await entity_existence_service.exists(company) is True


@pytest.mark.asyncio
async def test_register_company_company_already_exists(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company_factory_response = await company_factory.create_company(
        user_factory_response.user
    )
    assert await entity_existence_service.exists(company_factory_response) is True
    request_factory_response = RegisterCompanyRequestFactory.build().model_dump()

    request_factory_response.update({"name": company_factory_response.name.value})

    response = await test_client.post(
        "/companies/",
        json=request_factory_response,
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="Company with this name already exists",
        meta=[{"key": "name", "value": company_factory_response.name.value}],
    )
