from http import HTTPStatus
from typing import Final
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict, IsUUID
from httpx import AsyncClient

from prodik.domain.group import GroupId
from prodik.domain.node import NodeAssociationId
from tests.factories import (
    CompanyFactory,
    GroupFactory,
    NodeAssociationFactory,
    NodeFactory,
    UserFactory,
)
from tests.services import EntityExistenceService

NODES_COUNT: Final = 2


@pytest.mark.asyncio
async def test_attach_nodes_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    assert await entity_existence_service.exists(user_factory_response.user) is True
    company = await company_factory.create_company(user_factory_response.user)
    assert await entity_existence_service.exists(company) is True
    group = await group_factory.create_group(company=company)
    assert await entity_existence_service.exists(group) is True
    node_1 = await node_factory.create_node(company=company)
    assert await entity_existence_service.exists(node_1) is True
    node_2 = await node_factory.create_node(company=company)
    assert await entity_existence_service.exists(node_2) is True

    response = await test_client.post(
        "/nodes/attach",
        json={
            "group_id": str(group.id),
            "nodes": [str(node_1.id), str(node_2.id)],
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    result = response.json()
    assert len(result) == NODES_COUNT
    for item in result:
        assert item == IsPartialDict(
            id=IsUUID(),
            node_id=IsUUID(),
            group_id=str(group.id),
        )


@pytest.mark.asyncio
async def test_attach_nodes_group_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    assert await entity_existence_service.exists(user_factory_response.user) is True
    company = await company_factory.create_company(user_factory_response.user)
    assert await entity_existence_service.exists(company) is True
    node = await node_factory.create_node(company=company)
    assert await entity_existence_service.exists(node) is True

    response = await test_client.post(
        "/nodes/attach",
        json={
            "group_id": str(GroupId(uuid4())),
            "nodes": [str(node.id)],
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Group not found", meta=None)


@pytest.mark.asyncio
async def test_detach_node_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    node_association_factory: NodeAssociationFactory,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    assert await entity_existence_service.exists(user_factory_response.user) is True
    company = await company_factory.create_company(user_factory_response.user)
    assert await entity_existence_service.exists(company) is True
    group = await group_factory.create_group(company=company)
    assert await entity_existence_service.exists(group) is True
    node = await node_factory.create_node(company=company)
    assert await entity_existence_service.exists(node) is True
    association = await node_association_factory.create_association(
        node=node, group=group
    )
    assert await entity_existence_service.exists(association) is True

    response = await test_client.delete(
        f"/nodes/attach/{association.id}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_detach_node_association_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    assert await entity_existence_service.exists(user_factory_response.user) is True

    response = await test_client.delete(
        f"/nodes/attach/{NodeAssociationId(uuid4())}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Association not found error",
        meta=None,
    )


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
    assert await entity_existence_service.exists(user_factory_response.user) is True
    company = await company_factory.create_company(user_factory_response.user)
    assert await entity_existence_service.exists(company) is True
    node = await node_factory.create_node(company=company)
    assert await entity_existence_service.exists(node) is True
    group = await group_factory.create_group(company=company)
    assert await entity_existence_service.exists(group) is True
    association = await node_association_factory.create_association(
        node=node, group=group
    )
    assert await entity_existence_service.exists(association) is True

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
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    assert await entity_existence_service.exists(user_factory_response.user) is True
    company = await company_factory.create_company(user_factory_response.user)
    assert await entity_existence_service.exists(company) is True

    response = await test_client.delete(
        f"/nodes/{uuid4()}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Node not found",
        meta=None,
    )
