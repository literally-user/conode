from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDataclass, IsPartialDict
from httpx import AsyncClient

from conode.application.interfaces.repositories import NodeAssociationRepository
from tests.factories.common import authorization_headers
from tests.factories.models import (
    CompanyFactory,
    GroupFactory,
    NodeAssociationFactory,
    NodeFactory,
    UserFactory,
)

# Отсоединение ноды от группы это:


@pytest.mark.asyncio
async def test_detach_node_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    group_factory: GroupFactory,
    node_association_factory: NodeAssociationFactory,
    node_association_repository: NodeAssociationRepository,
) -> None:
    user = await user_factory.build()
    company = await company_factory.build(owner=user.user)
    group = await group_factory.build(company=company)
    additional_group = await group_factory.build(company=company)
    node, association = await node_factory.build(company=company, group=group)
    additional_association = await node_association_factory.build(
        node=node, group=additional_group
    )

    response = await transport.delete(
        f"/nodes/associations/{additional_association.id}",
        headers=authorization_headers(user.access_token),
    )

    associations = await node_association_repository.get_all_by_node_id(node.id)

    assert len(associations) == 1
    assert associations[0] == IsPartialDataclass(id=association.id)
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_detach_node_have_single_association(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    group_factory: GroupFactory,
    node_association_repository: NodeAssociationRepository,
) -> None:
    user = await user_factory.build()
    company = await company_factory.build(owner=user.user)
    group = await group_factory.build(company=company)
    node, association = await node_factory.build(company=company, group=group)

    response = await transport.delete(
        f"/nodes/associations/{association.id}",
        headers=authorization_headers(user.access_token),
    )

    associations = await node_association_repository.get_all_by_node_id(node.id)

    assert len(associations) == 1
    assert associations[0] == IsPartialDataclass(id=association.id)
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="Node must have at least one association",
        meta=[{"key": "node_association_id", "value": str(association.node_id)}],
    )


@pytest.mark.asyncio
async def test_detach_node_user_without_correct_rights(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    group_factory: GroupFactory,
    node_association_repository: NodeAssociationRepository,
) -> None:
    users = (await user_factory.build(), await user_factory.build())
    company = await company_factory.build(owner=users[1].user)
    group = await group_factory.build(company=company)
    node, association = await node_factory.build(company=company, group=group)

    response = await transport.delete(
        f"/nodes/associations/{association.id}",
        headers=authorization_headers(users[0].access_token),
    )

    associations = await node_association_repository.get_all_by_node_id(node.id)

    assert len(associations) == 1
    assert associations[0] == IsPartialDataclass(id=association.id)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation", meta=None
    )
