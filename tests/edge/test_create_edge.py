from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    ContextFactory,
    CreateEdgeRequestFactory,
    GroupFactory,
    NodeFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_create_edge_ok(
    user_factory: UserFactory,
    context_factory: ContextFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user=user_factory_response.user)
    context = await context_factory.create_context(company=company)
    nodes = [await node_factory.create_node(company=company) for _ in range(2)]

    response = await test_client.post(
        "/edges/",
        json=CreateEdgeRequestFactory.build(
            node_a_id=nodes[0].id,
            node_b_id=nodes[1].id,
            context_id=context.id,
        ).model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        id=IsStr(),
        node_a_id=str(nodes[0].id),
        node_b_id=str(nodes[1].id),
        context_id=str(context.id),
        company_id=str(company.id),
    )


@pytest.mark.asyncio
async def test_create_edge_context_not_found(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user=user_factory_response.user)
    group = await group_factory.create_group(company=company)
    nodes = [
        await node_factory.create_node(
            user=user_factory_response.user,
            company=company,
            group=group,
        )
        for _ in range(2)
    ]
    fake_context_id = uuid4()

    response = await test_client.post(
        "/edges/",
        json=CreateEdgeRequestFactory.build(
            node_a_id=nodes[0].id,
            node_b_id=nodes[1].id,
            context_id=fake_context_id,
        ).model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Context not found",
        meta=[{"key": "context_id", "value": str(fake_context_id)}],
    )


@pytest.mark.asyncio
async def test_create_edge_context_forbidden(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    context_factory: ContextFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user=user_factory_response.user)
    another_company = await company_factory.create_company()
    context = await context_factory.create_context(company=another_company)
    group = await group_factory.create_group(company=company)
    nodes = [
        await node_factory.create_node(
            user=user_factory_response.user,
            group=group,
            company=company,
        )
        for _ in range(2)
    ]

    response = await test_client.post(
        "/edges/",
        json=CreateEdgeRequestFactory.build(
            node_a_id=nodes[0].id,
            node_b_id=nodes[1].id,
            context_id=context.id,
        ).model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
