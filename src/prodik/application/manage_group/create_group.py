from dataclasses import dataclass
from uuid import uuid4

import structlog

from prodik.application.errors import (
    CompanyNotFoundError,
    GroupNotFoundError,
    UserNotFoundError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    GroupRepository,
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.group import Group, GroupId

logger = structlog.get_logger()


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateGroupRequestDTO:
    name: str
    description: str
    parent_group_id: GroupId | None


@dataclass
class CreateGroupInteractor:
    company_repository: CompanyRepository
    user_repository: UserRepository
    group_repository: GroupRepository
    identity_provider: IdentityProvider
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, request: CreateGroupRequestDTO) -> Group:
        async with self.transaction_manager:
            user_meta = self.identity_provider.get_current_user_meta()

            logger.info("Received user meta")

            user = await self.user_repository.get_by_id(user_meta["user_id"])
            if user is None:
                raise UserNotFoundError("User not found", None)

            logger.info("Received user", user_id=user.id)

            self.access_control_service.ensure_revision_is_valid(user_meta, user)

            company = await self.company_repository.get_by_user_id(user.id)
            if company is None:
                raise CompanyNotFoundError("User must have at least one company", None)

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
