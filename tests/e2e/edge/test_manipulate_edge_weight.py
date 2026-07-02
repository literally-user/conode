from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDataclass, IsPartialDict
from httpx import AsyncClient

from prodik.application.interfaces.repositories import EdgeRepository
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
async def test_increment_edge_weight_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    edge_factory: EdgeFactory,
    context_factory: ContextFactory,
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
    edge = await edge_factory.build(
        node_a=nodes[0], node_b=nodes[1], context=context, company=company
    )

    response = await transport.patch(
        f"/edges/{edge.id}/weight/increment",
        headers=authorization_headers(user.access_token),
    )
    edges = await edge_repository.get_all_by_context_id(context.id)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert edges[0] == IsPartialDataclass(weight=edge.weight + 1)


@pytest.mark.asyncio
async def test_decrement_edge_weight_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    edge_factory: EdgeFactory,
    context_factory: ContextFactory,
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
    edge = await edge_factory.build(
        node_a=nodes[0], node_b=nodes[1], context=context, company=company, weight=5
    )

    response = await transport.patch(
        f"/edges/{edge.id}/weight/decrement",
        headers=authorization_headers(user.access_token),
    )
    edges = await edge_repository.get_all_by_context_id(context.id)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert edges[0] == IsPartialDataclass(weight=edge.weight - 1)


@pytest.mark.asyncio
async def test_update_edge_weight_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    edge_factory: EdgeFactory,
    context_factory: ContextFactory,
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
    edge = await edge_factory.build(
        node_a=nodes[0], node_b=nodes[1], context=context, company=company
    )

    response = await transport.patch(
        f"/edges/{edge.id}/weight",
        json={"weight": 100},
        headers=authorization_headers(user.access_token),
    )
    edges = await edge_repository.get_all_by_context_id(context.id)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert edges[0] == IsPartialDataclass(weight=100)


@pytest.mark.asyncio
async def test_increment_edge_weight_user_without_correct_rights(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    edge_factory: EdgeFactory,
    context_factory: ContextFactory,
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
    edge = await edge_factory.build(
        node_a=nodes[0],
        node_b=nodes[1],
        context=context,
        company=company,
    )

    response = await transport.patch(
        f"/edges/{edge.id}/weight/increment",
        headers=authorization_headers(users[1].access_token),
    )

    edges = await edge_repository.get_all_by_context_id(context.id)

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert edges[0] == IsPartialDataclass(weight=edge.weight)
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )


@pytest.mark.asyncio
async def test_decrement_edge_weight_user_without_correct_rights(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    edge_factory: EdgeFactory,
    context_factory: ContextFactory,
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
    edge = await edge_factory.build(
        node_a=nodes[0],
        node_b=nodes[1],
        context=context,
        company=company,
        weight=5,
    )

    response = await transport.patch(
        f"/edges/{edge.id}/weight/decrement",
        headers=authorization_headers(users[1].access_token),
    )

    edges = await edge_repository.get_all_by_context_id(context.id)

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert edges[0] == IsPartialDataclass(weight=edge.weight)
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )


@pytest.mark.asyncio
async def test_update_edge_weight_user_without_correct_rights(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    edge_factory: EdgeFactory,
    context_factory: ContextFactory,
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
    edge = await edge_factory.build(
        node_a=nodes[0],
        node_b=nodes[1],
        context=context,
        company=company,
    )

    response = await transport.patch(
        f"/edges/{edge.id}/weight",
        json={"weight": 100},
        headers=authorization_headers(users[1].access_token),
    )

    edges = await edge_repository.get_all_by_context_id(context.id)

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert edges[0] == IsPartialDataclass(weight=edge.weight)
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
