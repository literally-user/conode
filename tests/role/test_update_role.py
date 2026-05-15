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
    UpdatePermissionRequestFactory,
    UpdateRoleRequestFactory,
    UserFactory,
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

    request = UpdateRoleRequestFactory.build(permissions={})

    response = await test_client.put(
        f"/roles/{role.id}",
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == IsPartialDict(
        role=IsPartialDict(
            id=IsStr(),
            owner_company_id=str(company.id),
            name=request.name,
        ),
        permissions=[],
    )


@pytest.mark.asyncio
async def test_update_role_not_found(
    user_factory: UserFactory,
    test_client: AsyncClient,
) -> None:
    user_factory_response = await user_factory.create_user(admin=True)
    fake_role_id = uuid4()

    response = await test_client.put(
        f"/roles/{fake_role_id}",
        json=UpdateRoleRequestFactory.build(permissions={}).model_dump(mode="json"),
        headers={"Authorization": f"Bearer {user_factory_response.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == IsPartialDict(
        detail="Role not found",
        meta=[{"key": "role_id", "value": str(fake_role_id)}],
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
        json=UpdateRoleRequestFactory.build(permissions={}).model_dump(mode="json"),
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
        json=UpdateRoleRequestFactory.build(
            name=role.name.value,
            permissions={
                permission.id: UpdatePermissionRequestFactory.build(
                    permission=PermissionType.MODIFY,
                    entity_type=EntityType.COMPANY,
                    entity_id=company.id,
                ),
            },
        ).model_dump(mode="json"),
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
