from dataclasses import dataclass
from uuid import uuid4

from conode.application.interfaces.repositories import (
    CompanyRepository,
    ContextRepository,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AccessControlService
from conode.domain.company import CompanyId
from conode.domain.context import Context, ContextId


@dataclass
class CreateContextRequestDTO:
    name: str
    description: str
    company_id: CompanyId


@dataclass
class CreateContextInteractor:
    transaction_manager: TransactionManager
    company_repository: CompanyRepository
    context_repository: ContextRepository
    access_control_service: AccessControlService

    async def execute(self, request: CreateContextRequestDTO) -> Context:
        user = await self.access_control_service.get_authorized_user()

        async with self.transaction_manager:
            company = await self.company_repository.get_by_id(request.company_id)

            await self.access_control_service.ensure_user_can_create_contexts(
                user,
                company,
            )

            context = Context.new(
                context_id=ContextId(uuid4()),
                name=request.name,
                description=request.description,
                company=company,
            )

            await self.context_repository.create(context)

            return context
