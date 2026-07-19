from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
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


@pytest.mark.asyncio
async def test_delete_edge_ok(
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

    response = await transport.delete(
        f"/edges/{edge.id}", headers=authorization_headers(user.access_token)
    )
    edges = await edge_repository.get_all_by_context_id(context.id)

    assert len(edges) == 0
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_edge_user_without_correct_rights(
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
        node_a=nodes[0], node_b=nodes[1], context=context, company=company
    )

    response = await transport.delete(
        f"/edges/{edge.id}", headers=authorization_headers(users[1].access_token)
    )
    edges = await edge_repository.get_all_by_context_id(context.id)

    assert len(edges) == 1
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
