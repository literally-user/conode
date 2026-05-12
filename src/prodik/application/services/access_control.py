import asyncio
from dataclasses import dataclass

from prodik.application.errors import (
    NotEnoughRightsError,
    SessionExpiredError,
    UserNotFoundError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    RolePermissionsRepository,
    RoleRepository,
    UserRepository,
)
from prodik.application.interfaces.token_managers import UserMeta
from prodik.domain.company import Company
from prodik.domain.context import Context
from prodik.domain.group import Group
from prodik.domain.role import (
    EntityType,
    PermissionType,
    RolePermission,
    RolePermissionEntityId,
)
from prodik.domain.user import User

type RolesPermissions = list[list[RolePermission]]


@dataclass
class AccessControlService:
    role_permissions_repository: RolePermissionsRepository
    role_repository: RoleRepository
    identity_provider: IdentityProvider
    user_repository: UserRepository

    def _ensure_revision_is_valid(self, meta: UserMeta, user: User) -> None:
        if meta["revision"] != user.token_revision:
            raise SessionExpiredError("Session has expired", None)

    async def _get_all_permissions(self, user: User) -> RolesPermissions:
        roles = await self.role_repository.get_all_by_user_id(user.id)
        return await asyncio.gather(
            *[
                self.role_permissions_repository.get_all_by_role_id(role.id)
                for role in roles
            ]
        )

    def _find_permission(
        self,
        permissions: RolesPermissions,
        permission_type: PermissionType,
        entity_type: EntityType,
        entity_id: RolePermissionEntityId,
    ) -> bool:
        return any(
            permission.permission == permission_type
            and permission.entity_type == entity_type
            and permission.entity_id == entity_id
            for role_permissions in permissions
            for permission in role_permissions
        )

    async def get_authorized_user(self) -> User:
        meta = self.identity_provider.get_current_user_meta()

        user = await self.user_repository.get_by_id(meta["user_id"])
        if user is None:
            raise UserNotFoundError("User not found", None)

        self._ensure_revision_is_valid(meta, user)

        return user

    async def ensure_user_can_create_contexts(
        self, executor: User, target_company: Company
    ) -> None:
        permissions = await self._get_all_permissions(executor)

        if self._find_permission(
            permissions, PermissionType.MODIFY, EntityType.COMPANY, target_company.id
        ):
            return

        raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_manipulate_context(
        self, executor: User, context: Context
    ) -> None:
        permissions = await self._get_all_permissions(executor)

        if self._find_permission(
            permissions, PermissionType.MODIFY, EntityType.COMPANY, context.company_id
        ):
            return

        if self._find_permission(
            permissions, PermissionType.MODIFY, EntityType.CONTEXT, context.id
        ):
            return

        raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_create_groups(
        self, executor: User, target_company: Company
    ) -> None:
        permissions = await self._get_all_permissions(executor)

        if self._find_permission(
            permissions, PermissionType.MODIFY, EntityType.COMPANY, target_company.id
        ):
            return

        raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_manipulate_group(
        self, executor: User, group: Group
    ) -> None:
        permissions = await self._get_all_permissions(executor)

        if self._find_permission(
            permissions, PermissionType.MODIFY, EntityType.COMPANY, group.company_id
        ):
            return

        if self._find_permission(
            permissions, PermissionType.MODIFY, EntityType.GROUP, group.id
        ):
            return

        raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_view_context(
        self, executor: User, context: Context
    ) -> None:
        permissions = await self._get_all_permissions(executor)

        if self._find_permission(
            permissions, PermissionType.MODIFY, EntityType.COMPANY, context.company_id
        ):
            return

        if self._find_permission(
            permissions, PermissionType.MODIFY, EntityType.CONTEXT, context.id
        ):
            return

        if self._find_permission(
            permissions, PermissionType.READ, EntityType.CONTEXT, context.id
        ):
            return

        raise NotEnoughRightsError("Not enough rights to perform operation", None)

    async def ensure_user_can_view_group(self, executor: User, group: Group) -> None:
        permissions = await self._get_all_permissions(executor)

        if self._find_permission(
            permissions, PermissionType.MODIFY, EntityType.COMPANY, group.company_id
        ):
            return

        if self._find_permission(
            permissions, PermissionType.MODIFY, EntityType.GROUP, group.id
        ):
            return

        if self._find_permission(
            permissions, PermissionType.READ, EntityType.GROUP, group.id
        ):
            return

        raise NotEnoughRightsError("Not enough rights to perform operation", None)
