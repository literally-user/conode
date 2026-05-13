from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from tests.factories import (
    CompanyFactory,
    RoleFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_give_role_to_user_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    role_factory: RoleFactory,
    test_client: AsyncClient,
) -> None:
    executor_response = await user_factory.create_user(admin=False)

    company = await company_factory.create_company(user=executor_response.user)

    role = await role_factory.create_role(company=company)

    target_user = (await user_factory.create_user()).user

    response = await test_client.post(
        f"/users/{target_user.id}/roles/{role.id}",
        headers={"Authorization": f"Bearer {executor_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_give_role_to_user_role_not_found(
    user_factory: UserFactory,
    test_client: AsyncClient,
) -> None:
    executor_response = await user_factory.create_user(admin=True)

    target_user = (await user_factory.create_user()).user

    response = await test_client.post(
        f"/users/{target_user.id}/roles/{uuid4()}",
        headers={"Authorization": f"Bearer {executor_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == IsPartialDict(
        detail="Role not found",
        meta=None,
    )


@pytest.mark.asyncio
async def test_give_role_to_user_user_not_found(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    role_factory: RoleFactory,
    test_client: AsyncClient,
) -> None:
    executor_response = await user_factory.create_user(admin=False)

    company = await company_factory.create_company(user=executor_response.user)

    role = await role_factory.create_role(company=company)

    response = await test_client.post(
        f"/users/{uuid4()}/roles/{role.id}",
        headers={"Authorization": f"Bearer {executor_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == IsPartialDict(
        detail="User not found",
        meta=None,
    )


@pytest.mark.asyncio
async def test_give_role_to_user_forbidden(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    role_factory: RoleFactory,
    test_client: AsyncClient,
) -> None:
    another_company = await company_factory.create_company()

    role = await role_factory.create_role(company=another_company)

    executor_response = await user_factory.create_user(admin=False)

    target_user = (await user_factory.create_user()).user

    response = await test_client.post(
        f"/users/{target_user.id}/roles/{role.id}",
        headers={"Authorization": f"Bearer {executor_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )


@pytest.mark.asyncio
async def test_give_role_to_user_grant_already_exists(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    role_factory: RoleFactory,
    test_client: AsyncClient,
) -> None:
    executor_response = await user_factory.create_user(admin=False)

    company = await company_factory.create_company(user=executor_response.user)

    role = await role_factory.create_role(company=company)

    response = await test_client.post(
        f"/users/{executor_response.user.id}/roles/{role.id}",
        headers={"Authorization": f"Bearer {executor_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="Grant already exists",
        meta=None,
    )
