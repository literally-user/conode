from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDataclass, IsPartialDict
from httpx import AsyncClient

from conode.application.interfaces.repositories import EdgeRepository
from tests.factories.common import authorization_headers
from tests.factories.models import (
    CompanyFactory,
    ContextFactory,
    EdgeFactory,
    GroupFactory,
    NodeFactory,
    UserFactory,
)
from tests.factories.schemas import CreateEdgeRequestFactory


@pytest.mark.asyncio
async def test_create_edge_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_factory: ContextFactory,
    node_factory: NodeFactory,
    group_factory: GroupFactory,
    edge_repository: EdgeRepository,
) -> None:
    user = await user_factory.build()
    company = await company_factory.build(owner=user.user)
    context = await context_factory.build(company=company)
    group = await group_factory.build(company=company)
    nodes = (
        (await node_factory.build(group=group, company=company))[0],
        (await node_factory.build(group=group, company=company))[0],
    )

    request = CreateEdgeRequestFactory.build(
        context_id=context.id, node_a_id=nodes[0].id, node_b_id=nodes[1].id
    )

    response = await transport.post(
        "/edges/",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(user.access_token),
    )
    content = response.json()

    edges = await edge_repository.get_all_by_context_id(context.id)

    assert len(edges) == 1
    assert response.status_code == HTTPStatus.CREATED
    assert edges[0] == IsPartialDataclass(
        node_a_id=nodes[0].id,
        node_b_id=nodes[1].id,
        context_id=context.id,
        company_id=company.id,
    )
    assert content == IsPartialDict(
        id=str(edges[0].id),
        node_a_id=str(edges[0].node_a_id),
        node_b_id=str(edges[0].node_b_id),
        context_id=str(edges[0].context_id),
        company_id=str(edges[0].company_id),
    )


@pytest.mark.asyncio
async def test_create_edge_user_without_correct_rights(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_factory: ContextFactory,
    node_factory: NodeFactory,
    group_factory: GroupFactory,
    edge_repository: EdgeRepository,
) -> None:
    users = (await user_factory.build(), await user_factory.build())
    company = await company_factory.build(owner=users[0].user)
    context = await context_factory.build(company=company)
    group = await group_factory.build(company=company)
    nodes = (
        (await node_factory.build(group=group, company=company))[0],
        (await node_factory.build(group=group, company=company))[0],
    )

    request = CreateEdgeRequestFactory.build(
        context_id=context.id, node_a_id=nodes[0].id, node_b_id=nodes[1].id
    )

    response = await transport.post(
        "/edges/",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(users[1].access_token),
    )

    edges = await edge_repository.get_all_by_context_id(context.id)

    assert len(edges) == 0
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )


@pytest.mark.asyncio
async def test_create_edge_already_exists(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_factory: ContextFactory,
    node_factory: NodeFactory,
    edge_factory: EdgeFactory,
    group_factory: GroupFactory,
    edge_repository: EdgeRepository,
) -> None:
    user = await user_factory.build()
    company = await company_factory.build(owner=user.user)
    context = await context_factory.build(company=company)
    group = await group_factory.build(company=company)
    nodes = (
        (await node_factory.build(group=group, company=company))[0],
        (await node_factory.build(group=group, company=company))[0],
    )
    await edge_factory.build(
        node_a=nodes[0], node_b=nodes[1], context=context, company=company
    )

    request = CreateEdgeRequestFactory.build(
        context_id=context.id, node_a_id=nodes[0].id, node_b_id=nodes[1].id
    )

    response = await transport.post(
        "/edges/",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(user.access_token),
    )

    edges = await edge_repository.get_all_by_context_id(context.id)

    assert len(edges) == 1
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="Edge between nodes in this context already exists",
        meta=[
            {"key": "node_a_id", "value": str(request.node_a_id)},
            {"key": "node_b_id", "value": str(request.node_b_id)},
            {"key": "context_id", "value": str(request.context_id)},
        ],
    )
