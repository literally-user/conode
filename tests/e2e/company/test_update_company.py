from http import HTTPStatus

import pytest
from httpx import AsyncClient

from tests.factories.common import authorization_headers
from tests.factories.models import CompanyFactory, UserFactory
from tests.factories.schemas import UpdateCompanyRequestFactory


@pytest.mark.asyncio
async def test_update_company_ok(
    transport: AsyncClient, user_factory: UserFactory, company_factory: CompanyFactory
) -> None:
    user = await user_factory.build()
    company = await company_factory.build(owner=user.user)

    request = UpdateCompanyRequestFactory.build()

    response = await transport.put(
        f"/companies/{company.id}",
        json=request.model_dump(),
        headers=authorization_headers(user.access_token),
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_update_company_without_corrent_rights(
    transport: AsyncClient, user_factory: UserFactory, company_factory: CompanyFactory
) -> None:
    users = (await user_factory.build(), await user_factory.build())
    company = await company_factory.build(owner=users[0].user)

    request = UpdateCompanyRequestFactory.build()

    response = await transport.put(
        f"/companies/{company.id}",
        json=request.model_dump(),
        headers=authorization_headers(users[1].access_token),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
