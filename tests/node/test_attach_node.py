from http import HTTPStatus
from typing import Final
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict, IsUUID
from httpx import AsyncClient

from prodik.application.interfaces.repositories import NodeAssociationRepository
from prodik.domain.node import NodeAssociationId
from tests.factories import CompanyFactory, GroupFactory, NodeFactory, UserFactory
from tests.services import EntityExistenceService

EXPECTED_NODES_COUNT: Final = 2


@pytest.mark.asyncio
async def test_attach_nodes_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    node_association_repository: NodeAssociationRepository,
    entity_existence_service: EntityExistenceService,
) -> None:
    user = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user.user)
    group = await group_factory.create_group(company=company)
    node_1 = await node_factory.create_node(company=company)
    node_2 = await node_factory.create_node(company=company)

    response = await test_client.post(
        "/nodes/attach",
        json={
            "group_id": str(group.id),
            "nodes": [str(node_1.id), str(node_2.id)],
        },
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    result = response.json()
    assert len(result) == EXPECTED_NODES_COUNT
    for item in result:
        assert item == IsPartialDict(
            id=IsUUID(),
            node_id=IsUUID(),
            group_id=str(group.id),
        )
        association = await node_association_repository.get_by_id(
            NodeAssociationId(item["id"])
        )
        assert association is not None
        assert await entity_existence_service.exists(association) is True


@pytest.mark.asyncio
async def test_attach_nodes_group_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
) -> None:
    user = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user.user)
    node = await node_factory.create_node(company=company)

    response = await test_client.post(
        "/nodes/attach",
        json={"group_id": str(uuid4()), "nodes": [str(node.id)]},
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Group not found", meta=None)


@pytest.mark.asyncio
async def test_attach_nodes_company_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    company_factory: CompanyFactory,
) -> None:
    owner = await user_factory.create_user(admin=False)
    owner_company = await company_factory.create_company(owner.user)
    group = await group_factory.create_group(company=owner_company)
    node = await node_factory.create_node(company=owner_company)

    executor = await user_factory.create_user(admin=False)

    response = await test_client.post(
        "/nodes/attach",
        json={"group_id": str(group.id), "nodes": [str(node.id)]},
        headers={"Authorization": f"Bearer {executor.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Company not found", meta=None)


@pytest.mark.asyncio
async def test_attach_nodes_forbidden(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
) -> None:
    owner = await user_factory.create_user(admin=False)
    owner_company = await company_factory.create_company(owner.user)
    node = await node_factory.create_node(company=owner_company)

    executor = await user_factory.create_user(admin=False)
    executor_company = await company_factory.create_company(executor.user)
    executor_group = await group_factory.create_group(company=executor_company)

    response = await test_client.post(
        "/nodes/attach",
        json={"group_id": str(executor_group.id), "nodes": [str(node.id)]},
        headers={"Authorization": f"Bearer {executor.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
