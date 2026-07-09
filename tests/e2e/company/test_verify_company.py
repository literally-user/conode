from http import HTTPStatus

import pytest
from httpx import AsyncClient

from prodik.application.interfaces.repositories import CompanyRepository
from tests.factories.common import authorization_headers
from tests.factories.models import CompanyFactory, UserFactory


@pytest.mark.asyncio
async def test_verify_company_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    company_repository: CompanyRepository,
) -> None:
    user_factory_response = await user_factory.build(admin=True)

    company = await company_factory.build(owner=user_factory_response.user)

    response = await transport.patch(
        f"/companies/{company.id}/verify",
        headers=authorization_headers(user_factory_response.access_token),
    )

    company = await company_repository.get_by_id(company.id)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert company.verified


@pytest.mark.asyncio
async def test_verify_company_user_not_admin(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    company_repository: CompanyRepository,
) -> None:
    user_factory_response = await user_factory.build()

    company = await company_factory.build(owner=user_factory_response.user)

    response = await transport.patch(
        f"/companies/{company.id}/verify",
        headers=authorization_headers(user_factory_response.access_token),
    )
    company = await company_repository.get_by_id(company.id)

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert not company.verified
