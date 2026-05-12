from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from prodik.domain.node import NodeAssociationId
from tests.factories import (
    CompanyFactory,
    GroupFactory,
    NodeAssociationFactory,
    NodeFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_detach_node_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    node_association_factory: NodeAssociationFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    group = await group_factory.create_group(company=company)
    node = await node_factory.create_node(company=company)
    association = await node_association_factory.create_association(
        node=node, group=group
    )

    response = await test_client.delete(
        f"/nodes/attach/{association.id}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_detach_node_association_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    await company_factory.create_company(user_factory_response.user)

    response = await test_client.delete(
        f"/nodes/attach/{NodeAssociationId(uuid4())}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Association not found error", meta=None
    )


@pytest.mark.asyncio
async def test_detach_node_forbidden(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    node_association_factory: NodeAssociationFactory,
) -> None:
    owner = await user_factory.create_user(admin=False)
    owner_company = await company_factory.create_company(owner.user)
    owner_group = await group_factory.create_group(company=owner_company)
    owner_node = await node_factory.create_node(company=owner_company)
    association = await node_association_factory.create_association(
        node=owner_node, group=owner_group
    )

    executor = await user_factory.create_user(admin=False)
    await company_factory.create_company(executor.user)

    response = await test_client.delete(
        f"/nodes/attach/{association.id}",
        headers={"Authorization": f"Bearer {executor.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation", meta=None
    )
