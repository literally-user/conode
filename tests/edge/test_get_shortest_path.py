from http import HTTPStatus
from random import choice

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
async def test_get_shortest_path_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_factory: ContextFactory,
    group_factory: GroupFactory,
    edge_factory: EdgeFactory,
    node_factory: NodeFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user=user_factory_response.user)
    group = await group_factory.create_group(company)
    nodes = [
        await node_factory.create_node(
            company=company, group=group, user=user_factory_response.user
        )
        for _ in range(4)
    ]
    context = await context_factory.create_context(company=company)

    await edge_factory.generate_random_graph(nodes, company, context, 1.0)

    response = await test_client.get(
        "/edges/shortest",
        params={
            "from_node_id": str(choice(nodes).id),
            "to_node_id": str(choice(nodes).id),
            "context_id": str(context.id),
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
