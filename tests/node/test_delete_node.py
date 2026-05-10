from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    GroupFactory,
    NodeAssociationFactory,
    NodeFactory,
    UserFactory,
)
from tests.services import EntityExistenceService


@pytest.mark.asyncio
async def test_delete_node_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    node_factory: NodeFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_association_factory: NodeAssociationFactory,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    node = await node_factory.create_node(company=company)
    group = await group_factory.create_group(company=company)
    association = await node_association_factory.create_association(
        node=node, group=group, company=company
    )

    response = await test_client.delete(
        f"/nodes/{node.id}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert await entity_existence_service.exists(node) is False
    assert await entity_existence_service.exists(association) is False


@pytest.mark.asyncio
async def test_delete_node_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    await company_factory.create_company(user_factory_response.user)

    response = await test_client.delete(
        f"/nodes/{uuid4()}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Node not found", meta=None)


@pytest.mark.asyncio
async def test_delete_node_forbidden(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
) -> None:
    owner = await user_factory.create_user(admin=False)
    owner_company = await company_factory.create_company(owner.user)
    node = await node_factory.create_node(company=owner_company)

    executor = await user_factory.create_user(admin=False)
    await company_factory.create_company(executor.user)

    response = await test_client.delete(
        f"/nodes/{node.id}",
        headers={"Authorization": f"Bearer {executor.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation", meta=None
    )
