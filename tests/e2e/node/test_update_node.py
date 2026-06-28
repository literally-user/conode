from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDataclass, IsPartialDict
from httpx import AsyncClient

from prodik.application.interfaces.repositories import NodeRepository
from prodik.domain.node import NodeDescription, NodeName
from tests.factories.common import authorization_headers
from tests.factories.models import (
    CompanyFactory,
    GroupFactory,
    NodeFactory,
    UserFactory,
)
from tests.factories.schemas.node import UpdateNodeRequestFactory


@pytest.mark.asyncio
async def test_update_node_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    node_repository: NodeRepository,
) -> None:
    user = await user_factory.build()
    company = await company_factory.build(owner=user.user)
    group = await group_factory.build(company=company)
    node = await node_factory.build(company=company, group=group)

    request = UpdateNodeRequestFactory.build()

    response = await transport.put(
        f"/nodes/{node.id}",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(user.access_token),
    )

    node = await node_repository.get_by_id(node.id)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert node == IsPartialDataclass(
        name=NodeName(request.name),
        description=NodeDescription(request.description),
    )


@pytest.mark.asyncio
async def test_update_node_user_without_correct_rights(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    node_repository: NodeRepository,
) -> None:
    users = (await user_factory.build(), await user_factory.build())
    company = await company_factory.build(owner=users[0].user)
    group = await group_factory.build(company=company)
    node = await node_factory.build(company=company, group=group)

    request = UpdateNodeRequestFactory.build()

    response = await transport.put(
        f"/nodes/{node.id}",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(users[1].access_token),
    )

    node = await node_repository.get_by_id(node.id)

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
