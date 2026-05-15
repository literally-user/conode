from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories import (
    AttachNodeRequestFactory,
    CompanyFactory,
    GroupFactory,
    NodeFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_attach_node_ok(
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
        str((await node_factory.create_node(company=company)).id) for _ in range(10)
    ]

    response = await test_client.post(
        "/nodes/attach",
        json=AttachNodeRequestFactory.build(
            group_id=group.id,
            nodes=nodes,
        ).model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert len(response.json()) == len(nodes)


@pytest.mark.asyncio
async def test_attach_node_group_not_found(
    user_factory: UserFactory,
    test_client: AsyncClient,
    company_factory: CompanyFactory,
    node_factory: NodeFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user=user_factory_response.user)

    nodes = [
        str((await node_factory.create_node(company=company)).id) for _ in range(10)
    ]
    fake_group_id = uuid4()

    response = await test_client.post(
        "/nodes/attach",
        json=AttachNodeRequestFactory.build(
            group_id=fake_group_id,
            nodes=nodes,
        ).model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Group not found",
        meta=[{"key": "group_id", "value": str(fake_group_id)}],
    )


@pytest.mark.asyncio
async def test_attach_node_forbidden(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    user_company = await company_factory.create_company(user_factory_response.user)

    another_company = await company_factory.create_company()
    another_group = await group_factory.create_group(company=another_company)

    nodes = [
        str((await node_factory.create_node(company=user_company)).id)
        for _ in range(10)
    ]

    response = await test_client.post(
        "/nodes/attach",
        json=AttachNodeRequestFactory.build(
            group_id=another_group.id,
            nodes=nodes,
        ).model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation", meta=None
    )
