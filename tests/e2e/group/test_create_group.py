from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict, IsStr
from httpx import AsyncClient

from conode.application.interfaces.repositories import GroupRepository
from tests.factories.common import authorization_headers
from tests.factories.models import CompanyFactory, GroupFactory, UserFactory
from tests.factories.schemas import CreateGroupRequestFactory


@pytest.mark.asyncio
async def test_create_group_ok(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_repository: GroupRepository,
) -> None:
    user_factory_response = await user_factory.build()

    company = await company_factory.build(owner=user_factory_response.user)

    request = CreateGroupRequestFactory.build(
        parent_group_id=None, company_id=company.id
    )

    response = await transport.post(
        "/groups/",
        headers=authorization_headers(user_factory_response.access_token),
        json=request.model_dump(mode="json"),
    )

    groups = await group_repository.get_all_by_company_id(company.id)

    assert len(groups) == 1
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        id=IsStr,
        name=request.name,
        description=request.description,
        company_id=str(company.id),
        parent_group_id=None,
    )


@pytest.mark.asyncio
async def test_create_group_without_correct_rights(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_repository: GroupRepository,
) -> None:
    users = (
        await user_factory.build(),
        await user_factory.build(),
    )

    company = await company_factory.build(owner=users[1].user)

    request = CreateGroupRequestFactory.build(
        parent_group_id=None, company_id=company.id
    )

    response = await transport.post(
        "/groups/",
        headers=authorization_headers(users[0].access_token),
        json=request.model_dump(mode="json"),
    )

    groups = await group_repository.get_all_by_company_id(company.id)

    assert len(groups) == 0
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )


@pytest.mark.asyncio
async def test_create_group_with_parent(
    transport: AsyncClient,
    user_factory: UserFactory,
    group_factory: GroupFactory,
    company_factory: CompanyFactory,
    group_repository: GroupRepository,
) -> None:
    user_factory_response = await user_factory.build()

    company = await company_factory.build(owner=user_factory_response.user)
    parent_group = await group_factory.build(company=company)

    request = CreateGroupRequestFactory.build(
        parent_group_id=parent_group.id, company_id=company.id
    )

    response = await transport.post(
        "/groups/",
        headers=authorization_headers(user_factory_response.access_token),
        json=request.model_dump(mode="json"),
    )
    content = response.json()

    group = await group_repository.get_by_id(content["id"])

    assert group.parent_group_id == parent_group.id
    assert response.status_code == HTTPStatus.CREATED
    assert content == IsPartialDict(
        id=IsStr,
        name=request.name,
        description=request.description,
        company_id=str(company.id),
        parent_group_id=str(parent_group.id),
    )


@pytest.mark.asyncio
async def test_create_group_with_parent_not_exists(
    transport: AsyncClient,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_repository: GroupRepository,
) -> None:
    user_factory_response = await user_factory.build()

    company = await company_factory.build(owner=user_factory_response.user)

    fake_group_id = uuid4()
    request = CreateGroupRequestFactory.build(
        parent_group_id=fake_group_id, company_id=company.id
    )

    response = await transport.post(
        "/groups/",
        headers=authorization_headers(user_factory_response.access_token),
        json=request.model_dump(mode="json"),
    )

    groups = await group_repository.get_all_by_company_id(company.id)

    assert len(groups) == 0
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Group not found",
        meta=[{"key": "group_id", "value": str(fake_group_id)}],
    )
