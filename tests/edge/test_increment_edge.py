from http import HTTPStatus

import pytest
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    ContextFactory,
    EdgeFactory,
    NodeFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_increment_edge_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_factory: ContextFactory,
    edge_factory: EdgeFactory,
    node_factory: NodeFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user=user_factory_response.user)
    nodes = [await node_factory.create_node(company=company) for _ in range(2)]
    context = await context_factory.create_context(company=company)
    edge = await edge_factory.create_edge(
        node_a=nodes[0],
        node_b=nodes[1],
        company=company,
        context=context,
    )

    response = await test_client.patch(
        f"/edges/{edge.id}/weight/increment",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
