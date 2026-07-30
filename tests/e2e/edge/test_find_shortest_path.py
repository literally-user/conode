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
async def test_find_shortest_path_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    context_factory: ContextFactory,
    edge_factory: EdgeFactory,
    node_factory: NodeFactory,
) -> None:
    user = await user_factory.build()
    company = await company_factory.build(owner=user.user)
    group = await group_factory.build(company=company)
    context = await context_factory.build(company=company)

    nodes = (
        (await node_factory.build(company=company, group=group))[0],
        (await node_factory.build(company=company, group=group))[0],
        (await node_factory.build(company=company, group=group))[0],
        (await node_factory.build(company=company, group=group))[0],
    )

    # Simple graph where shortest path
    # from nodes[0] to nodes[3] goes through edges[0] -> edges[-1]
    edges = (
        await edge_factory.build(
            company=company, context=context, node_a=nodes[0], node_b=nodes[1], weight=4
        ),
        await edge_factory.build(
            company=company, context=context, node_a=nodes[0], node_b=nodes[2], weight=3
        ),
        await edge_factory.build(
            company=company, context=context, node_a=nodes[0], node_b=nodes[3], weight=7
        ),
        await edge_factory.build(
            company=company, context=context, node_a=nodes[2], node_b=nodes[1], weight=2
        ),
        await edge_factory.build(
            company=company, context=context, node_a=nodes[1], node_b=nodes[3], weight=1
        ),
    )

    response = await transport.get(
        "/edges/shortest",
        params={
            "from_node_id": str(nodes[0].id),
            "to_node_id": str(nodes[3].id),
            "context_id": str(context.id),
        },
        headers=authorization_headers(user.access_token),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        IsPartialDict(
            id=str(edges[0].id),
            node_a_id=str(nodes[0].id),
            node_b_id=str(nodes[1].id),
            context_id=str(context.id),
            company_id=str(company.id),
        ),
        IsPartialDict(
            id=str(edges[-1].id),
            node_a_id=str(nodes[1].id),
            node_b_id=str(nodes[3].id),
            context_id=str(context.id),
            company_id=str(company.id),
        ),
    ]


@pytest.mark.asyncio
async def test_find_shortest_path_didnt_exists(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    context_factory: ContextFactory,
    node_factory: NodeFactory,
) -> None:
    user = await user_factory.build()
    company = await company_factory.build(owner=user.user)
    group = await group_factory.build(company=company)
    context = await context_factory.build(company=company)

    nodes = (
        (await node_factory.build(company=company, group=group))[0],
        (await node_factory.build(company=company, group=group))[0],
    )

    response = await transport.get(
        "/edges/shortest",
        params={
            "from_node_id": str(nodes[0].id),
            "to_node_id": str(nodes[1].id),
            "context_id": str(context.id),
        },
        headers=authorization_headers(user.access_token),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []
