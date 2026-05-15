from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict, IsStr
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    CreateNodeRequestFactory,
    GroupFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_create_node_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    company = await company_factory.create_company(user=user_factory_response.user)
    group = await group_factory.create_group(company=company)

    request = CreateNodeRequestFactory.build(group_id=group.id)

    response = await test_client.post(
        "/nodes/",
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        id=IsStr(),
        name=request.name,
        description=request.description,
        company_id=str(company.id),
    )


@pytest.mark.asyncio
async def test_create_node_group_not_found(
    user_factory: UserFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)
    fake_group_id = uuid4()

    response = await test_client.post(
        "/nodes/",
        json=CreateNodeRequestFactory.build(group_id=fake_group_id).model_dump(
            mode="json"
        ),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Group not found",
        meta=[{"key": "group_id", "value": str(fake_group_id)}],
    )


@pytest.mark.asyncio
async def test_create_node_forbidden(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    group_factory: GroupFactory,
    test_client: AsyncClient,
) -> None:
    company = await company_factory.create_company()
    group = await group_factory.create_group(company)

    user_factory_response = await user_factory.create_user()

    response = await test_client.post(
        "/nodes/",
        json=CreateNodeRequestFactory.build(name="abcde", group_id=group.id).model_dump(
            mode="json"
        ),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation", meta=None
    )
