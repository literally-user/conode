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
async def test_update_node_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    node = await node_factory.create_node(company=company)

    response = await test_client.put(
        f"/nodes/{node.id}",
        json={
            "name": "NEWNODENAME123",
            "description": "VERYVERYVERYNEWNEWNEWAMAZINGDESCRIPTION",
        },
        headers={
            "Authorization": f"Bearer {user_factory_response.access_token}",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        id=str(node.id),
        name="NEWNODENAME123",
        description="VERYVERYVERYNEWNEWNEWAMAZINGDESCRIPTION",
    )


@pytest.mark.asyncio
async def test_update_node_forbidden(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    await company_factory.create_company(user_factory_response.user)

    company = await company_factory.create_company()
    node = await node_factory.create_node(company=company)

    response = await test_client.put(
        f"/nodes/{node.id}",
        json={
            "name": "NEWNODENAME123",
            "description": "VERYVERYVERYNEWNEWNEWAMAZINGDESCRIPTION",
        },
        headers={
            "Authorization": f"Bearer {user_factory_response.access_token}",
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
