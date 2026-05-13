from dataclasses import dataclass

import structlog
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import (
    RolePermissionsRepository,
)
from prodik.domain.role import RolePermission
from prodik.domain.role.model import RoleId

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
            permissions_count=len(permissions),
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
        permissions = list(result.scalars().all())
        logger.info(
            "Repository fetched permissions by role id",
            role_id=role_id,
            count=len(permissions),
        )

        return permissions
