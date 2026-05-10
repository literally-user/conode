from http import HTTPStatus
from uuid import uuid4

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
from tests.services import EntityExistenceService


@pytest.mark.asyncio
async def test_delete_edge_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    context_factory: ContextFactory,
    edge_factory: EdgeFactory,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    node_a = await node_factory.create_node(company=company)
    node_b = await node_factory.create_node(company=company)
    context = await context_factory.create_context(company=company)
    edge = await edge_factory.create_edge(
        node_a=node_a, node_b=node_b, company=company, context=context, weight=2
    )

    response = await test_client.delete(
        f"/edges/{edge.id}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert await entity_existence_service.exists(edge) is False


@pytest.mark.asyncio
async def test_delete_edge_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    await company_factory.create_company(user_factory_response.user)

    response = await test_client.delete(
        f"/edges/{uuid4()}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Edge not found", meta=None)


@pytest.mark.asyncio
async def test_delete_edge_forbidden(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    context_factory: ContextFactory,
    edge_factory: EdgeFactory,
) -> None:
    owner = await user_factory.create_user(admin=False)
    owner_company = await company_factory.create_company(owner.user)
    owner_node_a = await node_factory.create_node(company=owner_company)
    owner_node_b = await node_factory.create_node(company=owner_company)
    owner_context = await context_factory.create_context(company=owner_company)
    edge = await edge_factory.create_edge(
        node_a=owner_node_a,
        node_b=owner_node_b,
        company=owner_company,
        context=owner_context,
        weight=1,
    )

    executor = await user_factory.create_user(admin=False)
    await company_factory.create_company(executor.user)

    response = await test_client.delete(
        f"/edges/{edge.id}",
        headers={"Authorization": f"Bearer {executor.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation", meta=None
    )
