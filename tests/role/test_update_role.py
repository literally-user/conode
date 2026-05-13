from http import HTTPStatus
from uuid import uuid4

import pytest
from dirty_equals import IsPartialDict, IsStr
from httpx import AsyncClient

from prodik.application.interfaces.repositories import RolePermissionsRepository
from prodik.domain.role import EntityType, PermissionType
from tests.factories import (
    CompanyFactory,
    RoleFactory,
    UserFactory,
    generate_random_string,
)


@pytest.mark.asyncio
async def test_update_role_ok(
    role_factory: RoleFactory,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)

    company = await company_factory.create_company(user=user_factory_response.user)

    role = await role_factory.create_role(company=company)

    new_name = generate_random_string(10)

    response = await test_client.put(
        f"/roles/{role.id}",
        json={
            "name": new_name,
            "permissions": {},
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == IsPartialDict(
        role=IsPartialDict(
            id=IsStr(),
            owner_company_id=str(company.id),
            name=new_name,
        ),
        permissions=[],
    )


@pytest.mark.asyncio
async def test_update_role_not_found(
    user_factory: UserFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=True)

    response = await test_client.put(
        f"/roles/{uuid4()}",
        json={
            "name": generate_random_string(10),
            "permissions": {},
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == IsPartialDict(
        detail="Role not found",
        meta=None,
    )


@pytest.mark.asyncio
async def test_update_role_forbidden(
    role_factory: RoleFactory,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
) -> None:
    another_company = await company_factory.create_company()

    role = await role_factory.create_role(company=another_company)

    user_factory_response = await user_factory.create_user(admin=False)

    response = await test_client.put(
        f"/roles/{role.id}",
        json={
            "name": generate_random_string(10),
            "permissions": {},
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation",
        meta=None,
    )


@pytest.mark.asyncio
async def test_update_role_permissions_ok(
    role_factory: RoleFactory,
    user_factory: UserFactory,
    company_factory: CompanyFactory,
    test_client: AsyncClient,
    role_permissions_repository: RolePermissionsRepository,
) -> None:
    user_factory_response = await user_factory.create_user(admin=False)

    company = await company_factory.create_company(user=user_factory_response.user)

    role = await role_factory.create_role(company=company)

    permissions = await role_permissions_repository.get_all_by_role_id(role.id)

    permission = permissions[0]

    response = await test_client.put(
        f"/roles/{role.id}",
        json={
            "name": role.name.value,
            "permissions": {
                str(permission.id): {
                    "permission": PermissionType.MODIFY,
                    "entity_type": EntityType.COMPANY,
                    "entity_id": str(company.id),
                }
            },
        },
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body == IsPartialDict(
        role=IsPartialDict(
            id=str(role.id),
            owner_company_id=str(company.id),
            name=role.name.value,
        ),
    )

    assert len(body["permissions"]) > 0

    updated_permission = body["permissions"][0]

    assert updated_permission == IsPartialDict(
        role_id=str(role.id),
        permission=PermissionType.MODIFY,
        entity_type=EntityType.COMPANY,
        entity_id=str(company.id),
    )
