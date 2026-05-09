from http import HTTPStatus
from typing import Final
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from prodik.application.interfaces.repositories import EdgeRepository
from tests.factories import (
    CompanyFactory,
    ContextFactory,
    EdgeFactory,
    NodeFactory,
    UserFactory,
)
from tests.services import EntityExistenceService

EXPECTED_WEIGHT: Final = 42.5


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
        node_a=node_a,
        node_b=node_b,
        company=company,
        context=context,
        weight=2,
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
async def test_increment_edge_weight_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    context_factory: ContextFactory,
    edge_factory: EdgeFactory,
    edge_repository: EdgeRepository,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    node_a = await node_factory.create_node(company=company)
    node_b = await node_factory.create_node(company=company)
    context = await context_factory.create_context(company=company)
    edge = await edge_factory.create_edge(
        node_a=node_a,
        node_b=node_b,
        company=company,
        context=context,
        weight=0,
    )

    response = await test_client.patch(
        f"/edges/{edge.id}/weight/increment",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    updated_edge = await edge_repository.get_by_id(edge.id)
    assert updated_edge is not None
    assert updated_edge.weight == 1


@pytest.mark.asyncio
async def test_decrement_edge_weight_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    context_factory: ContextFactory,
    edge_factory: EdgeFactory,
    edge_repository: EdgeRepository,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    node_a = await node_factory.create_node(company=company)
    node_b = await node_factory.create_node(company=company)
    context = await context_factory.create_context(company=company)
    edge = await edge_factory.create_edge(
        node_a=node_a,
        node_b=node_b,
        company=company,
        context=context,
        weight=2,
    )

    response = await test_client.patch(
        f"/edges/{edge.id}/weight/decrement",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    updated_edge = await edge_repository.get_by_id(edge.id)
    assert updated_edge is not None
    assert updated_edge.weight == 1


@pytest.mark.asyncio
async def test_update_edge_weight_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
    context_factory: ContextFactory,
    edge_factory: EdgeFactory,
    edge_repository: EdgeRepository,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    node_a = await node_factory.create_node(company=company)
    node_b = await node_factory.create_node(company=company)
    context = await context_factory.create_context(company=company)
    edge = await edge_factory.create_edge(
        node_a=node_a,
        node_b=node_b,
        company=company,
        context=context,
        weight=1,
    )

    response = await test_client.patch(
        f"/edges/{edge.id}/weight",
        json={"weight": EXPECTED_WEIGHT},
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    updated_edge = await edge_repository.get_by_id(edge.id)
    assert updated_edge is not None
    assert updated_edge.weight == EXPECTED_WEIGHT


@pytest.mark.asyncio
async def test_update_edge_weight_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    await company_factory.create_company(user_factory_response.user)

    response = await test_client.patch(
        f"/edges/{uuid4()}/weight",
        json={"weight": 11.0},
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Edge not found", meta=None)
