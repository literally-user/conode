from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    CreateRoleRequestFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_create_role_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=True)
    company = await company_factory.create_company(user=user_factory_response.user)

    request = CreateRoleRequestFactory.build(
        company_id=company.id,
    )

    response = await test_client.post(
        "/roles/",
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        id=IsStr(),
        owner_company_id=str(company.id),
        name=request.name,
    )
