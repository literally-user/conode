from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict, IsStr
from httpx import AsyncClient

from prodik.application.interfaces.repositories import (
    CompanyRepository,
    RoleRepository,
    UserGrantRepository,
)
from tests.e2e.helpers.asserts import assert_user_have_correct_rights
from tests.factories.common import authorization_headers
from tests.factories.models import CompanyFactory, UserFactory
from tests.factories.schemas import RegisterCompanyRequestFactory


@pytest.mark.asyncio
async def test_register_company_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    role_repository: RoleRepository,
    company_repository: CompanyRepository,
    user_grant_repository: UserGrantRepository,
) -> None:
    user_factory_response = await user_factory.build()

    request = RegisterCompanyRequestFactory.build()

    response = await transport.post(
        "/companies/",
        headers=authorization_headers(user_factory_response.access_token),
        json=request.model_dump(),
    )
    content = response.json()

    assert response.status_code == HTTPStatus.CREATED
    await assert_user_have_correct_rights(
        content,
        user_factory_response.user,
        user_grant_repository,
        company_repository,
        role_repository,
    )
    assert content == IsPartialDict(
        id=IsStr,
        name=request.name,
        owner_id=str(user_factory_response.user.id),
        description=request.description,
        verified=False,
    )


@pytest.mark.asyncio
async def test_register_company_while_same_company_exists(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    user_grant_repository: UserGrantRepository,
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

    grants = await user_grant_repository.get_all_by_user_id(
        user_factory_response.user.id
    )

    assert len(grants) == 1
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="Company with this name already exists",
        meta=[{"key": "name", "value": request.name}],
    )
