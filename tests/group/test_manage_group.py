from http import HTTPStatus
from uuid import UUID, uuid4

import pytest
from dirty_equals import IsPartialDict, IsUUID
from httpx import AsyncClient

from prodik.application.interfaces.repositories import GroupRepository
from prodik.domain.group import GroupId
from tests.factories import (
    CompanyFactory,
    GroupFactory,
    NodeAssociationFactory,
    NodeFactory,
    UserFactory,
)
from tests.services import EntityExistenceService


@pytest.mark.asyncio
async def test_create_group_ok(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_repository: GroupRepository,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    await company_factory.create_company(user_factory_response.user)

    response = await test_client.post(
        "/groups/",
        json={
            "name": "new-group",
            "description": "group for tests",
            "parent_group_id": None,
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        id=IsUUID(),
        name="new-group",
        description="group for tests",
        company_id=IsUUID(),
        parent_group_id=None,
    )
    group = await group_repository.get_by_id(GroupId(UUID(response.json()["id"])))
    assert group is not None
    assert await entity_existence_service.exists(group) is True


@pytest.mark.asyncio
async def test_delete_group_ok_and_cascade_association(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    node_factory: NodeFactory,
    node_association_factory: NodeAssociationFactory,
    entity_existence_service: EntityExistenceService,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user_factory_response.user)
    group = await group_factory.create_group(company=company)
    node = await node_factory.create_node(company=company)
    association = await node_association_factory.create_association(
        node=node, group=group, company=company
    )

    response = await test_client.delete(
        f"/groups/{group.id}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert await entity_existence_service.exists(group) is False
    assert await entity_existence_service.exists(association) is False


@pytest.mark.asyncio
async def test_delete_group_not_found(
    test_client: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    await company_factory.create_company(user_factory_response.user)

    response = await test_client.delete(
        f"/groups/{uuid4()}",
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Group not found",
        meta=None,
    )
