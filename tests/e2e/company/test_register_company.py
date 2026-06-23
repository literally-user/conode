from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories.common import authorization_headers
from tests.factories.models import CompanyFactory, UserFactory
from tests.factories.schemas import RegisterCompanyRequestFactory


@pytest.mark.asyncio
async def test_register_company_ok(
    transport: AsyncClient, user_factory: UserFactory
) -> None:
    user_factory_response = await user_factory.build()

    request = RegisterCompanyRequestFactory.build()

    response = await transport.post(
        "/companies/",
        headers=authorization_headers(user_factory_response.access_token),
        json=request.model_dump(),
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        id=IsStr,
        name=request.name,
        owner_id=str(user_factory_response.user.id),
        description=request.description,
        verified=False,
    )


@pytest.mark.asyncio
async def test_register_company_while_same_company_exists(
    transport: AsyncClient, user_factory: UserFactory, company_factory: CompanyFactory
) -> None:
    user_factory_response = await user_factory.build()

    company = await company_factory.build(owner=user_factory_response.user)

    request = RegisterCompanyRequestFactory.build(
        name=company.name.value,
        description=company.description.value,
    )

    response = await transport.post(
        "/companies/",
        headers=authorization_headers(user_factory_response.access_token),
        json=request.model_dump(),
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="Company with this name already exists",
        meta=[{"key": "name", "value": request.name}],
    )
