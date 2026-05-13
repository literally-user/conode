from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    NodeFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_delete_node_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user=user_factory_response.user)
    node = await node_factory.create_node(company=company)

    response = await test_client.delete(
        f"/nodes/{node.id}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_node_forbidden(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    test_client: AsyncClient,
) -> None:
    company = await company_factory.create_company()
    node = await node_factory.create_node(company=company)

    user_factory_response = await user_factory.create_user(admin=False)

    response = await test_client.delete(
        f"/nodes/{node.id}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation", meta=None
    )
