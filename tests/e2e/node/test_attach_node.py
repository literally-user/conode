from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from prodik.application.interfaces.repositories import (
    NodeAssociationRepository,
)
from tests.factories.common import authorization_headers
from tests.factories.models import (
    CompanyFactory,
    GroupFactory,
    NodeFactory,
    UserFactory,
)
from tests.factories.schemas import AttachNodeRequestFactory

# 1. Проверка прав


@pytest.mark.asyncio
async def test_attach_node_ok(
    transport: AsyncClient,
    node_association_repository: NodeAssociationRepository,
    user_factory: UserFactory,
    node_factory: NodeFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
) -> None:
    user_factory_response = await user_factory.build()
    company = await company_factory.build(owner=user_factory_response.user)
    group_a = await group_factory.build(company=company)
    group_b = await group_factory.build(company=company)
    node, _ = await node_factory.build(group=group_a, company=company)

    request = AttachNodeRequestFactory.build(
        group_id=group_b.id,
        nodes=[node.id],
    )

    response = await transport.post(
        "/nodes/associations",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(user_factory_response.access_token),
    )

    node_associations = await node_association_repository.get_all_by_node_id(node.id)

    assert len(node_associations) == 2  # noqa: PLR2004
    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_attach_node_already_have_association(
    transport: AsyncClient,
    node_association_repository: NodeAssociationRepository,
    user_factory: UserFactory,
    node_factory: NodeFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
) -> None:
    user_factory_response = await user_factory.build()
    company = await company_factory.build(owner=user_factory_response.user)
    group = await group_factory.build(company=company)
    node, _ = await node_factory.build(group=group, company=company)

    request = AttachNodeRequestFactory.build(
        group_id=group.id,
        nodes=[node.id],
    )

    response = await transport.post(
        "/nodes/associations",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(user_factory_response.access_token),
    )

    node_associations = await node_association_repository.get_all_by_node_id(node.id)

    assert len(node_associations) == 1
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="Node cannot have same associations",
        meta=None,
    )


@pytest.mark.asyncio
async def test_attach_node_user_without_correct_rights(
    transport: AsyncClient,
    node_association_repository: NodeAssociationRepository,
    user_factory: UserFactory,
    node_factory: NodeFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
) -> None:
    users = (await user_factory.build(), await user_factory.build())
    company = await company_factory.build(owner=users[0].user)
    group = await group_factory.build(company=company)
    node, _ = await node_factory.build(group=group, company=company)

    request = AttachNodeRequestFactory.build(
        group_id=group.id,
        nodes=[node.id],
    )

    response = await transport.post(
        "/nodes/associations",
        json=request.model_dump(mode="json"),
        headers=authorization_headers(users[1].access_token),
    )

    node_associations = await node_association_repository.get_all_by_node_id(node.id)

    assert len(node_associations) == 1
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )
