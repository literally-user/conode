from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import CompanyNotFoundError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.context import Context, ContextId


@dataclass
class CreateContextRequestDTO:
    name: str
    description: str


@dataclass
class CreateContextInteractor:
    transaction_manager: TransactionManager
    identity_provider: IdentityProvider
    user_repository: UserRepository
    company_repository: CompanyRepository
    context_repository: ContextRepository
    access_control_service: AccessControlService

    async def execute(self, request: CreateContextRequestDTO) -> Context:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

            company = await self.company_repository.get_by_user_id(user.id)
            if company is None:
                raise CompanyNotFoundError("Company not found", None)

            context = Context.new(
                id=ContextId(uuid4()),
                name=request.name,
                description=request.description,
                company=company,
            )

            await self.context_repository.create(context)

            return context
