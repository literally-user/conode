from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories import CompanyFactory, RegisterCompanyRequestFactory, UserFactory


@pytest.mark.asyncio
async def test_register_company_ok(
    user_factory: UserFactory, test_client: AsyncClient
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
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


@pytest.mark.asyncio
async def test_register_company_company_already_exists(
    user_factory: UserFactory, company_factory: CompanyFactory, test_client: AsyncClient
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company_factory_response = await company_factory.create_company(
        user_factory_response.user
    )
    request_factory_response = RegisterCompanyRequestFactory.build().model_dump()

    request_factory_response.update({"name": company_factory_response.name.value})

    response = await test_client.post(
        "/companies/",
        json=request_factory_response,
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="Company already exists",
        meta=[{"key": "name", "value": company_factory_response.name.value}],
    )
