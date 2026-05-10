from dataclasses import dataclass

from prodik.application.errors import (
    CompanyNotFoundError,
    ContextNotFoundError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.context import ContextId


@dataclass
class DeleteContextInteractor:
    user_repository: UserRepository
    company_repository: CompanyRepository
    context_repository: ContextRepository
    identity_provider: IdentityProvider
    access_control_service: AccessControlService
    transaction_manager: TransactionManager

    async def execute(self, context_id: ContextId) -> None:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            company = await self.company_repository.get_by_user_id(user.id)
            if company is None:
                raise CompanyNotFoundError("Company not found", None)

            context = await self.context_repository.get_by_id(context_id)
            if context is None:
                raise ContextNotFoundError("Context not found", None)

            self.access_control_service.ensure_user_can_manipulate_context(
                user,
                company,
                context,
            )

            await self.context_repository.delete(context)
