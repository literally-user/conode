from dataclasses import dataclass

from conode.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService
from conode.domain.context import ContextId


@dataclass
class DeleteContextInteractor:
    company_repository: CompanyRepository
    context_repository: ContextRepository
    access_control_service: AccessControlService
    transaction_manager: TransactionManager

    async def execute(self, context_id: ContextId) -> None:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            context = await self.context_repository.get_by_id(context_id)

            await self.access_control_service.ensure_user_can_manipulate_context(
                user,
                context,
            )

            await self.context_repository.delete(context)
