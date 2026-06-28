from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDataclass, IsPartialDict, IsStr
from httpx import AsyncClient

from prodik.application.interfaces.repositories import NodeRepository
from prodik.domain.node import NodeDescription, NodeName
from tests.factories.common import authorization_headers
from tests.factories.models import CompanyFactory, GroupFactory, UserFactory
from tests.factories.schemas import CreateNodeRequestFactory


@pytest.mark.asyncio
async def test_create_node_ok(
    transport: AsyncClient,
    node_repository: NodeRepository,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
) -> None:
    user_factory_response = await user_factory.build()
    company = await company_factory.build(owner=user_factory_response.user)
    group = await group_factory.build(company=company)

    request = CreateNodeRequestFactory.build(group_id=group.id)

    response = await transport.post(
        "/nodes/",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(user_factory_response.access_token),
    )
    content = response.json()

    node = await node_repository.get_by_id(content["id"])

    assert response.status_code == HTTPStatus.CREATED
    assert node == IsPartialDataclass(
        name=NodeName(request.name),
        description=NodeDescription(request.description),
    )
    assert content == IsPartialDict(
        id=IsStr,
        name=request.name,
        description=request.description,
        company_id=str(company.id),
    )


@pytest.mark.asyncio
async def test_create_node_without_correct_rights(
    transport: AsyncClient,
    node_repository: NodeRepository,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
) -> None:
    users = (await user_factory.build(), await user_factory.build())
    company = await company_factory.build(owner=users[0].user)
    group = await group_factory.build(company=company)

    request = CreateNodeRequestFactory.build(group_id=group.id)

    response = await transport.post(
        "/nodes/",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(users[1].access_token),
    )

    nodes = await node_repository.get_all_by_company_id(company.id)

    assert len(nodes) == 0
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
