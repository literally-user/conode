from http import HTTPStatus

import pytest
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    ContextFactory,
    EdgeFactory,
    GroupFactory,
    NodeFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_get_neighbours_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    edge_factory: EdgeFactory,
    node_factory: NodeFactory,
    group_factory: GroupFactory,
    context_factory: ContextFactory,
    company_factory: CompanyFactory,
) -> None:
    user_factory_response = await user_factory.create_user()
    company = await company_factory.create_company(user_factory_response.user)
    group = await group_factory.create_group(company)
    context = await context_factory.create_context(company)
    nodes = [
        await node_factory.create_node(group=group, company=company) for _ in range(4)
    ]

    for i in range(1, len(nodes)):
        await edge_factory.create_edge(
            node_a=nodes[0], node_b=nodes[i], company=company, context=context
        )

    response = await test_client.get(
        f"/nodes/{nodes[0].id}/neighbours",
        params={
            "context_id": str(context.id),
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == len(nodes) - 1
