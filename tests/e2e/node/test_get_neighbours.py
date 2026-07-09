from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories.common import authorization_headers
from tests.factories.models import (
    CompanyFactory,
    ContextFactory,
    EdgeFactory,
    GroupFactory,
    NodeFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_get_neighbours_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    edge_factory: EdgeFactory,
    context_factory: ContextFactory,
) -> None:
    user = await user_factory.build()
    company = await company_factory.build(owner=user.user)
    context = await context_factory.build(company=company)
    group = await group_factory.build(company=company)
    nodes = [
        (await node_factory.build(company=company, group=group))[0] for _ in range(5)
    ]
    [
        await edge_factory.build(
            node_a=nodes[0],
            node_b=nodes[index],
            context=context,
            company=company,
        )
        for index in range(1, len(nodes))
    ]

    response = await transport.get(
        f"/nodes/{nodes[1].id}/neighbours",
        params={"context_id": str(context.id), "depth": 2},
        headers=authorization_headers(user.access_token),
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == len(nodes) - 1


@pytest.mark.asyncio
async def test_get_neighbours_user_without_correct_rights(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_factory: ContextFactory,
) -> None:
    users = (await user_factory.build(), await user_factory.build())
    company = await company_factory.build(owner=users[0].user)
    context = await context_factory.build(company=company)

    response = await transport.get(
        f"/nodes/{context.id}/neighbours",
        params={"context_id": str(context.id), "depth": 2},
        headers=authorization_headers(users[1].access_token),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation", meta=None
    )
