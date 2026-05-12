from dataclasses import dataclass
from uuid import uuid4

import structlog

from prodik.application.errors import (
    CompanyNotFoundError,
    GroupNotFoundError,
)
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.company import CompanyId
from prodik.domain.group import Group, GroupId

logger = structlog.get_logger()


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateGroupRequestDTO:
    name: str
    description: str
    parent_group_id: GroupId | None
    company_id: CompanyId


@dataclass
class CreateGroupInteractor:
    company_repository: CompanyRepository
    group_repository: GroupRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, request: CreateGroupRequestDTO) -> Group:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            company = await self.company_repository.get_by_id(request.company_id)
            if company is None:
                raise CompanyNotFoundError("User must have at least one company", None)

            await self.access_control_service.ensure_user_can_create_groups(
                user,
                company,
            )

            parent_group = None
            if request.parent_group_id:
                parent_group = await self.group_repository.get_by_id(
                    request.parent_group_id
                )
                if parent_group is None:
                    raise GroupNotFoundError("Group not found", None)

            group = Group.new(
                id=GroupId(uuid4()),
                name=request.name,
                description=request.description,
                company=company,
                parent_group=parent_group if parent_group is not None else None,
            )

            await self.group_repository.create(group)

            return group
