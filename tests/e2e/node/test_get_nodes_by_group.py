from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories.common import authorization_headers
from tests.factories.models import (
    CompanyFactory,
    GroupFactory,
    NodeFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_get_nodes_by_group_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
) -> None:
    user = await user_factory.build()
    company = await company_factory.build(owner=user.user)
    group = await group_factory.build(company=company)
    nodes = [await node_factory.build(company=company, group=group) for _ in range(5)]

    response = await transport.get(
        f"/nodes/{group.id}",
        headers=authorization_headers(user.access_token),
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == len(nodes)


@pytest.mark.asyncio
async def test_get_nodes_by_group_user_without_correct_rights(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
) -> None:
    users = (await user_factory.build(), await user_factory.build())
    company = await company_factory.build(owner=users[0].user)
    group = await group_factory.build(company=company)

    response = await transport.get(
        f"/nodes/{group.id}",
        headers=authorization_headers(users[1].access_token),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
