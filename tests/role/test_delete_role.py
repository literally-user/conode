from http import HTTPStatus

import pytest
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    RoleFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_delete_role_ok(
    role_factory: RoleFactory,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    role = await role_factory.create_role(company=company)

    response = await test_client.delete(
        f"/roles/{role.id}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
