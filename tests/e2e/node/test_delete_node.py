from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from conode.application.interfaces.repositories import (
    NodeAssociationRepository,
    NodeRepository,
)
from tests.factories.common import authorization_headers
from tests.factories.models import (
    CompanyFactory,
    GroupFactory,
    NodeFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_delete_node_ok(
    transport: AsyncClient,
    node_factory: NodeFactory,
    group_factory: GroupFactory,
    company_factory: CompanyFactory,
    user_factory: UserFactory,
    node_repository: NodeRepository,
    node_association_repository: NodeAssociationRepository,
) -> None:
    user_factory_response = await user_factory.build()
    company = await company_factory.build(owner=user_factory_response.user)
    group = await group_factory.build(company=company)
    node, _ = await node_factory.build(company, group)

    response = await transport.delete(
        f"/nodes/{node.id}",
        headers=authorization_headers(user_factory_response.access_token),
    )

    nodes = await node_repository.get_all_by_company_id(company.id)
    node_associations = await node_association_repository.get_all_by_node_id(node.id)

    assert len(nodes) == 0
    assert len(node_associations) == 0
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_node_user_without_correct_rights(
    transport: AsyncClient,
    node_factory: NodeFactory,
    group_factory: GroupFactory,
    company_factory: CompanyFactory,
    user_factory: UserFactory,
    node_repository: NodeRepository,
    node_association_repository: NodeAssociationRepository,
) -> None:
    users = (await user_factory.build(), await user_factory.build())
    company = await company_factory.build(owner=users[0].user)
    group = await group_factory.build(company=company)
    node, _ = await node_factory.build(company, group)

    response = await transport.delete(
        f"/nodes/{node.id}", headers=authorization_headers(users[1].access_token)
    )

    nodes = await node_repository.get_all_by_company_id(company.id)
    node_associations = await node_association_repository.get_all_by_node_id(node.id)

    assert len(nodes) == 1
    assert len(node_associations) == 1
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
