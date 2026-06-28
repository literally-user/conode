from http import HTTPStatus

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from prodik.application.interfaces.repositories import GroupRepository
from tests.factories.common import authorization_headers
from tests.factories.models import CompanyFactory, GroupFactory, UserFactory


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
async def test_delete_group_user_have_not_access(
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
