import random
from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    ContextFactory,
    EdgeFactory,
    NodeFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_decrement_edge_ok(
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
        weight=random.randint(1, 100),
    )

    response = await test_client.patch(
        f"/edges/{edge.id}/weight/decrement",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_decrement_edge_weight_cannot_be_negative(
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
        node_a=nodes[0], node_b=nodes[1], company=company, context=context, weight=0
    )

    response = await test_client.patch(
        f"/edges/{edge.id}/weight/decrement",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="Edge weight cannot be negative", meta=None
    )
