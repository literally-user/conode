from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from prodik.application.interfaces.repositories import (
    GroupRepository,
    NodeAssociationRepository,
)
from tests.factories.common import authorization_headers
from tests.factories.models import (
    CompanyFactory,
    GroupFactory,
    NodeFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_delete_group_ok(
    transport: AsyncClient,
    group_repository: GroupRepository,
    group_factory: GroupFactory,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
) -> None:
    user_factory_response = await user_factory.build()
    company = await company_factory.build(owner=user_factory_response.user)
    group = await group_factory.build(company=company)

    response = await transport.delete(
        f"/groups/{group.id}",
        headers=authorization_headers(user_factory_response.access_token),
    )

    groups = await group_repository.get_all_by_company_id(company.id)

    assert len(groups) == 0
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_group_user_without_correct_rights(
    transport: AsyncClient,
    group_repository: GroupRepository,
    group_factory: GroupFactory,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
) -> None:
    users = (await user_factory.build(), await user_factory.build())
    company = await company_factory.build(owner=users[0].user)
    group = await group_factory.build(company=company)

    response = await transport.delete(
        f"/groups/{group.id}", headers=authorization_headers(users[1].access_token)
    )

    groups = await group_repository.get_all_by_company_id(company.id)

    assert len(groups) == 1
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )


@pytest.mark.asyncio
async def test_delete_group_with_childs(
    transport: AsyncClient,
    group_repository: GroupRepository,
    group_factory: GroupFactory,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
) -> None:
    user_factory_response = await user_factory.build()
    company = await company_factory.build(owner=user_factory_response.user)
    parent_group = await group_factory.build(company=company)

    await group_factory.build(company=company, parent_group=parent_group)

    response = await transport.delete(
        f"/groups/{parent_group.id}",
        headers=authorization_headers(user_factory_response.access_token),
    )

    groups = await group_repository.get_all_by_company_id(company.id)

    assert len(groups) == 0
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_group_with_associations(
    transport: AsyncClient,
    group_repository: GroupRepository,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    user_factory: UserFactory,
    node_association_repository: NodeAssociationRepository,
    company_factory: CompanyFactory,
) -> None:
    user_factory_response = await user_factory.build()

    company = await company_factory.build(owner=user_factory_response.user)
    group = await group_factory.build(company=company)
    node, _ = await node_factory.build(company=company, group=group)

    response = await transport.delete(
        f"/groups/{group.id}",
        headers=authorization_headers(user_factory_response.access_token),
    )

    groups = await group_repository.get_all_by_company_id(company.id)
    node_associations = await node_association_repository.get_all_by_node_id(node.id)

    assert len(groups) == 0
    assert len(node_associations) == 0
    assert response.status_code == HTTPStatus.NO_CONTENT
