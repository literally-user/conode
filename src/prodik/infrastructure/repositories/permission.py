from dataclasses import dataclass

import structlog
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import (
    RolePermissionsRepository,
)
from prodik.domain.role import RolePermission
from prodik.domain.role.model import RoleId, RolePermissionId

logger = structlog.get_logger()


@dataclass
class RolePermissionsRepositoryImpl(RolePermissionsRepository):
    session: AsyncSession

    async def create_all(
        self,
        permissions: list[RolePermission],
    ) -> None:
        if not permissions:
            return

        logger.info(
            "Repository create role permissions",
            request_count=len(permissions),
        )

        await self.session.execute(
            insert(RolePermission).values(
                [
                    {
                        "id": permission.id,
                        "role_id": permission.role_id,
                        "permission": permission.permission,
                        "entity_type": permission.entity_type,
                        "entity_id": permission.entity_id,
                        "created_at": permission.created_at,
                        "updated_at": permission.updated_at,
                    }
                    for permission in permissions
                ]
            )
        )

    async def get_all_by_role_id(
        self,
        role_id: RoleId,
    ) -> list[RolePermission]:
        logger.info(
            "Repository get permissions by role id",
            role_id=role_id,
        )

        result = await self.session.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id  # type: ignore
            )
        )
        result_permissions = list(result.scalars().all())
        logger.info(
            "Repository fetched permissions by role id",
            found_count=len(result_permissions),
        )

        return result_permissions

    async def update_all(self, permissions: list[RolePermission]) -> None:
        if not permissions:
            return

        logger.info(
            "Repository update role permissions",
            request_count=len(permissions),
        )

        for permission in permissions:
            await self.session.execute(
                update(RolePermission)
                .where(
                    RolePermission.id == permission.id  # type: ignore
                )
                .values(
                    permission=permission.permission,
                    entity_type=permission.entity_type,
                    entity_id=permission.entity_id,
                    updated_at=permission.updated_at,
                )
            )

    async def get_all_by_ids(
        self, permission_ids: list[RolePermissionId]
    ) -> list[RolePermission]:
        logger.info("Repository get nodes by ids", request_count=len(permission_ids))
        if not permission_ids:
            return []

        result = await self.session.execute(
            select(RolePermission).where(
                RolePermission.id.in_(permission_ids)  # type: ignore
            )
        )

        result_permissions = list(result.scalars().all())
        logger.info(
            "Repository fetched permissions by ids", found_count=len(result_permissions)
        )
        return result_permissions
