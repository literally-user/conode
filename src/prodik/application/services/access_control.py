import asyncio
from dataclasses import dataclass
from typing import Final

from prodik.application.errors import (
    CompanyNotFoundError,
    GroupNotFoundError,
    NotEnoughRightsError,
    SessionExpiredError,
    UserNotFoundError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    RolePermissionsRepository,
    RoleRepository,
    UserGrantRepository,
    UserRepository,
)
from prodik.application.interfaces.token_managers import UserMeta
from prodik.domain.company import Company
from prodik.domain.context import Context
from prodik.domain.group import Group
from prodik.domain.role import (
    EntityType,
    PermissionType,
    Role,
    RolePermission,
    RolePermissionEntityId,
)
from prodik.domain.user import User

type RolesPermissions = list[RolePermission]

PERMISSION_LEVEL: Final = {
    PermissionType.MODIFY: 2,
    PermissionType.READ: 1,
}


@dataclass
class AccessControlService:
    role_permissions_repository: RolePermissionsRepository
    user_grant_repository: UserGrantRepository
    role_repository: RoleRepository
    company_repository: CompanyRepository
    identity_provider: IdentityProvider
    user_repository: UserRepository

    def _ensure_revision_is_valid(self, meta: UserMeta, user: User) -> None:
        if meta["revision"] != user.token_revision:
            raise SessionExpiredError("Session has expired", None)

    async def _get_all_permissions(self, user: User) -> list[RolePermission]:
        grants = await self.user_grant_repository.get_all_by_user_id(user.id)
        role_ids = [g.role_id for g in grants]

        roles = await self.role_repository.get_all_by_ids(role_ids)

        role_permissions = await asyncio.gather(
            *[
                self.role_permissions_repository.get_all_by_role_id(role.id)
                for role in roles
            ]
        )

        return [p for group in role_permissions for p in group]

    async def get_authorized_user(self) -> User:
        meta = self.identity_provider.get_current_user_meta()

        user = await self.user_repository.get_by_id(meta["user_id"])
        if user is None:
            raise UserNotFoundError("User not found", None)

        self._ensure_revision_is_valid(meta, user)

        return user

    def check(
        self,
        *,
        permissions: RolesPermissions,
        required_permission: PermissionType,
        required_entity: EntityType,
        entity_id: RolePermissionEntityId | None,
        company: Company,
    ) -> bool:
        for perm in permissions:
            if (
                PERMISSION_LEVEL[perm.permission]
                < PERMISSION_LEVEL[required_permission]
            ):
                continue

            if perm.entity_type == EntityType.COMPANY and perm.entity_id == company.id:
                return True

            if (
                entity_id is not None
                and perm.entity_type == required_entity
                and perm.entity_id == entity_id
            ):
                return True

        return False

    async def ensure_user_can_manipulate_group(
        self,
        user: User,
        group: Group,
    ) -> None:
        permissions = await self._get_all_permissions(user)

        group_company = await self.company_repository.get_by_id(group.company_id)
        if group_company is None:
            raise GroupNotFoundError("Group company not found", None)

        if not self.check(
            permissions=permissions,
            required_permission=PermissionType.MODIFY,
            required_entity=EntityType.GROUP,
            entity_id=group.id,
            company=group_company,
        ):
            raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_manipulate_role(
        self,
        user: User,
        role: Role,
    ) -> None:
        permissions = await self._get_all_permissions(user)

        role_company = await self.company_repository.get_by_id(role.owner_company_id)
        if role_company is None:
            raise CompanyNotFoundError("Role company not found", None)

        if not self.check(
            permissions=permissions,
            required_permission=PermissionType.MODIFY,
            required_entity=EntityType.COMPANY,
            entity_id=None,
            company=role_company,
        ):
            raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_manipulate_context(
        self,
        user: User,
        context: Context,
    ) -> None:
        permissions = await self._get_all_permissions(user)

        context_company = await self.company_repository.get_by_id(context.company_id)
        if context_company is None:
            raise GroupNotFoundError("Context company not found", None)

        if not self.check(
            permissions=permissions,
            required_permission=PermissionType.MODIFY,
            required_entity=EntityType.GROUP,
            entity_id=context.id,
            company=context_company,
        ):
            raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_view_group(
        self,
        user: User,
        context: Group,
    ) -> None:
        permissions = await self._get_all_permissions(user)

        group_company = await self.company_repository.get_by_id(context.company_id)
        if group_company is None:
            raise GroupNotFoundError("Group company not found", None)

        if not self.check(
            permissions=permissions,
            required_permission=PermissionType.READ,
            required_entity=EntityType.GROUP,
            entity_id=context.id,
            company=group_company,
        ):
            raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_view_context(
        self,
        user: User,
        context: Context,
    ) -> None:
        permissions = await self._get_all_permissions(user)

        context_company = await self.company_repository.get_by_id(context.company_id)
        if context_company is None:
            raise GroupNotFoundError("Group company not found", None)

        if not self.check(
            permissions=permissions,
            required_permission=PermissionType.READ,
            required_entity=EntityType.CONTEXT,
            entity_id=context.id,
            company=context_company,
        ):
            raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_create_groups(
        self,
        user: User,
        target_company: Company,
    ) -> None:
        permissions = await self._get_all_permissions(user)

        if not self.check(
            permissions=permissions,
            required_permission=PermissionType.MODIFY,
            required_entity=EntityType.COMPANY,
            entity_id=None,
            company=target_company,
        ):
            raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_create_contexts(
        self,
        user: User,
        target_company: Company,
    ) -> None:
        permissions = await self._get_all_permissions(user)

        if not self.check(
            permissions=permissions,
            required_permission=PermissionType.MODIFY,
            required_entity=EntityType.COMPANY,
            entity_id=None,
            company=target_company,
        ):
            raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_create_roles(
        self,
        user: User,
        target_company: Company,
    ) -> None:
        permissions = await self._get_all_permissions(user)

        if not self.check(
            permissions=permissions,
            required_permission=PermissionType.MODIFY,
            required_entity=EntityType.COMPANY,
            entity_id=None,
            company=target_company,
        ):
            raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_send_offers(
        self,
        user: User,
        from_company: Company,
    ) -> None:
        permissions = await self._get_all_permissions(user)

        if not self.check(
            permissions=permissions,
            required_permission=PermissionType.MODIFY,
            required_entity=EntityType.COMPANY,
            entity_id=None,
            company=from_company,
        ):
            raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_manipulate_offers(
        self,
        user: User,
        to_company: Company,
    ) -> None:
        permissions = await self._get_all_permissions(user)

        if not self.check(
            permissions=permissions,
            required_permission=PermissionType.MODIFY,
            required_entity=EntityType.COMPANY,
            entity_id=None,
            company=to_company,
        ):
            raise NotEnoughRightsError("Not enough rights to perform operation", None)
