from http import HTTPStatus
from typing import Final
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict, IsStr, IsUUID
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    ContextFactory,
    EdgeFactory,
    NodeFactory,
    UserFactory,
)

EXPECTED_EDGES_COUNT: Final = 2


@pytest.mark.asyncio
async def test_get_edges_by_context_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_factory: ContextFactory,
    node_factory: NodeFactory,
    edge_factory: EdgeFactory,
) -> None:
    user = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user.user)
    context = await context_factory.create_context(company=company)
    node_1 = await node_factory.create_node(company=company)
    node_2 = await node_factory.create_node(company=company)
    await edge_factory.create_edge(node_1, node_2, company, context)

    response = await test_client.get(
        f"/edges/{context.id}",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    payload = response.json()
    assert len(payload) == EXPECTED_EDGES_COUNT
    assert {item["id"] for item in payload} == {str(node_1.id), str(node_2.id)}
    for item in payload:
        assert item == IsPartialDict(
            id=IsUUID(),
            name=IsStr(),
            description=IsStr(),
            company_id=str(company.id),
            created_at=IsStr(),
            updated_at=IsStr(),
        )


@pytest.mark.asyncio
async def test_get_edges_by_context_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
) -> None:
    user = await user_factory.create_user(admin=False)
    await company_factory.create_company(user.user)

    response = await test_client.get(
        f"/edges/{uuid4()}",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(detail="Context not found", meta=None)


@pytest.mark.asyncio
async def test_get_edges_by_context_forbidden(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    context_factory: ContextFactory,
) -> None:
    owner = await user_factory.create_user(admin=False)
    owner_company = await company_factory.create_company(owner.user)
    context = await context_factory.create_context(company=owner_company)

    executor = await user_factory.create_user(admin=False)
    await company_factory.create_company(executor.user)

    response = await test_client.get(
        f"/edges/{context.id}",
        headers={"Authorization": f"Bearer {executor.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
