from http import HTTPStatus
from typing import Final

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    ContextFactory,
    EdgeFactory,
    GroupFactory,
    NodeFactory,
    UserFactory,
)

DEPTH_TRIGGER: Final = 5


@pytest.mark.asyncio
async def test_get_direct_neighbours_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    edge_factory: EdgeFactory,
    node_factory: NodeFactory,
    group_factory: GroupFactory,
    context_factory: ContextFactory,
    company_factory: CompanyFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)

    company = await company_factory.create_company(user_factory_response.user)
    group = await group_factory.create_group(company)
    context = await context_factory.create_context(company)

    nodes = [
        await node_factory.create_node(
            company=company, group=group, user=user_factory_response.user
        )
        for _ in range(10)
    ]

    for i in range(1, len(nodes)):
        await edge_factory.create_edge(
            nodes[0], nodes[i], company=company, context=context
        )

    response = await test_client.get(
        f"/nodes/{nodes[0].id}/neighbours",
        params={
            "context_id": str(context.id),
            "depth": 1,
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == len(nodes) - 1


@pytest.mark.asyncio
async def test_get_deep_neighbours_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    edge_factory: EdgeFactory,
    node_factory: NodeFactory,
    group_factory: GroupFactory,
    context_factory: ContextFactory,
    company_factory: CompanyFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)

    company = await company_factory.create_company(user_factory_response.user)
    group = await group_factory.create_group(company)
    context = await context_factory.create_context(company)

    nodes = [
        await node_factory.create_node(
            company=company, group=group, user=user_factory_response.user
        )
        for _ in range(10)
    ]

    cursor = 0
    for i in range(1, len(nodes)):
        if i > DEPTH_TRIGGER:
            cursor += 1

        await edge_factory.create_edge(
            nodes[cursor], nodes[i], company=company, context=context
        )

    response = await test_client.get(
        f"/nodes/{nodes[0].id}/neighbours",
        params={
            "context_id": str(context.id),
            "depth": 2,
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == len(nodes)


@pytest.mark.asyncio
async def test_get_neighbours_depth_cannot_be_negative(
    test_client: AsyncClient,
    user_factory: UserFactory,
    node_factory: NodeFactory,
    context_factory: ContextFactory,
    company_factory: CompanyFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)

    company = await company_factory.create_company(user_factory_response.user)
    context = await context_factory.create_context(company)

    node = await node_factory.create_node(
        company=company, user=user_factory_response.user
    )

    response = await test_client.get(
        f"/nodes/{node.id}/neighbours",
        params={
            "context_id": str(context.id),
            "depth": -1,
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="Depth cannot be negative", meta=[{"key": "depth", "value": -1}]
    )
