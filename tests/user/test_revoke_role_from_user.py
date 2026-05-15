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
async def test_revoke_role_from_user_ok(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    role_factory: RoleFactory,
    test_client: AsyncClient,
) -> None:
    executor_response = await user_factory.create_user(admin=False)

    company = await company_factory.create_company(user=executor_response.user)

    role = await role_factory.create_role(company=company)

    target_user_response = await user_factory.create_user()

    await test_client.post(
        f"/users/{target_user_response.user.id}/roles/{role.id}",
        headers={"Authorization": f"Bearer {executor_response.access_token}"},
    )

    response = await test_client.delete(
        f"/users/{target_user_response.user.id}/roles/{role.id}",
        headers={"Authorization": f"Bearer {executor_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_revoke_role_from_user_role_not_found(
    user_factory: UserFactory,
    test_client: AsyncClient,
) -> None:
    executor_response = await user_factory.create_user(admin=True)

    target_user = (await user_factory.create_user()).user
    fake_role_id = uuid4()

    response = await test_client.delete(
        f"/users/{target_user.id}/roles/{fake_role_id}",
        headers={"Authorization": f"Bearer {executor_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == IsPartialDict(
        detail="Role not found",
        meta=[{"key": "role_id", "value": str(fake_role_id)}],
    )


@pytest.mark.asyncio
async def test_revoke_role_from_user_user_not_found(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    role_factory: RoleFactory,
    test_client: AsyncClient,
) -> None:
    executor_response = await user_factory.create_user(admin=False)

    company = await company_factory.create_company(user=executor_response.user)

    role = await role_factory.create_role(company=company)
    fake_user_id = uuid4()

    response = await test_client.delete(
        f"/users/{fake_user_id}/roles/{role.id}",
        headers={"Authorization": f"Bearer {executor_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == IsPartialDict(
        detail="User not found",
        meta=[{"key": "user_id", "value": str(fake_user_id)}],
    )


@pytest.mark.asyncio
async def test_revoke_role_from_user_forbidden(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    role_factory: RoleFactory,
    test_client: AsyncClient,
) -> None:
    another_company = await company_factory.create_company()

    role = await role_factory.create_role(company=another_company)

    executor_response = await user_factory.create_user(admin=False)

    target_user = (await user_factory.create_user()).user

    response = await test_client.delete(
        f"/users/{target_user.id}/roles/{role.id}",
        headers={"Authorization": f"Bearer {executor_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )


@pytest.mark.asyncio
async def test_revoke_role_from_user_grant_not_found(
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    role_factory: RoleFactory,
    test_client: AsyncClient,
) -> None:
    executor_response = await user_factory.create_user(admin=False)

    company = await company_factory.create_company(user=executor_response.user)

    role = await role_factory.create_role(company=company)

    target_user = (await user_factory.create_user()).user

    response = await test_client.delete(
        f"/users/{target_user.id}/roles/{role.id}",
        headers={"Authorization": f"Bearer {executor_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == IsPartialDict(
        detail="Grant by user and role id not found",
        meta=[
            {"key": "user_id", "value": str(target_user.id)},
            {"key": "role_id", "value": str(role.id)},
        ],
    )
