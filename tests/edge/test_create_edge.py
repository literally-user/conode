from datetime import datetime
from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict, IsStr, IsUUID
from httpx import AsyncClient

from prodik.domain.edge import Edge, EdgeId
from tests.factories import (
    CompanyFactory,
    ContextFactory,
    EdgeFactory,
    NodeFactory,
    UserFactory,
)
from tests.services import EntityExistenceService


@pytest.mark.asyncio
async def test_create_edge_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    context_factory: ContextFactory,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    node_a = await node_factory.create_node(company=company)
    node_b = await node_factory.create_node(company=company)
    context = await context_factory.create_context(company=company)

    response = await test_client.post(
        "/edges/",
        json={
            "node_a_id": str(node_a.id),
            "node_b_id": str(node_b.id),
            "context_id": str(context.id),
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        id=IsUUID(),
        node_a_id=str(node_a.id),
        node_b_id=str(node_b.id),
        context_id=str(context.id),
        company_id=str(company.id),
        created_at=IsStr(),
        updated_at=IsStr(),
    )

    payload = response.json()
    edge = Edge(
        id=EdgeId(payload["id"]),
        company_id=company.id,
        context_id=context.id,
        node_a_id=node_a.id,
        node_b_id=node_b.id,
        weight=0,
        created_at=datetime.fromisoformat(payload["created_at"]),
        updated_at=datetime.fromisoformat(payload["updated_at"]),
    )
    assert await entity_existence_service.exists(edge) is True


@pytest.mark.asyncio
async def test_create_edge_context_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    node_a = await node_factory.create_node(company=company)
    node_b = await node_factory.create_node(company=company)

    response = await test_client.post(
        "/edges/",
        json={
            "node_a_id": str(node_a.id),
            "node_b_id": str(node_b.id),
            "context_id": str(uuid4()),
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Context not found", meta=None)


@pytest.mark.asyncio
async def test_create_edge_already_exists(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    context_factory: ContextFactory,
    edge_factory: EdgeFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    context = await context_factory.create_context(company=company)
    node_a = await node_factory.create_node(company=company)
    node_b = await node_factory.create_node(company=company)
    await edge_factory.create_edge(node_a, node_b, company, context)

    response = await test_client.post(
        "/edges/",
        json={
            "node_a_id": str(node_a.id),
            "node_b_id": str(node_b.id),
            "context_id": str(context.id),
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="Edge between nodes in this context already exists",
        meta=[
            {"key": "node_a_id", "value": str(node_a.id)},
            {"key": "node_b_id", "value": str(node_b.id)},
            {"key": "context_id", "value": str(context.id)},
        ],
    )
