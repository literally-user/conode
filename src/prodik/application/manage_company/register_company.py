from dataclasses import dataclass
from uuid import uuid4

import structlog

from prodik.application.errors import CompanyAlreadyExistsError, UserNotFoundError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import CompanyRepository, UserRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import AccessControlService
from prodik.domain.company import Company, CompanyId, CompanyName

logger = structlog.get_logger()


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterCompanyRequestDTO:
    description: str
    name: str


@dataclass
class RegisterCompanyInteractor:
    identity_provider: IdentityProvider
    user_repository: UserRepository
    company_repository: CompanyRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, request: RegisterCompanyRequestDTO) -> Company:
        async with self.transaction_manager:
            user_meta = self.identity_provider.get_current_user_meta()

            logger.info("Received user meta")

            user = await self.user_repository.get_by_id(user_meta["user_id"])
            if user is None:
                raise UserNotFoundError("User not found", None)

            logger.info("Received user", user_id=user.id)

            self.access_control_service.ensure_revision_is_valid(user_meta, user)

            company = await self.company_repository.get_by_name(
                CompanyName(request.name)
            )
            if company is not None:
                raise CompanyAlreadyExistsError(
                    "Company with this name already exists",
                    [{"key": "name", "value": request.name}],
                )

            company = await self.company_repository.get_by_user_id(user.id)
            if company is not None:
                raise CompanyAlreadyExistsError(
                    "User can only have one company",
                    [{"key": "name", "value": request.name}],
                )

            company = Company.new(
                id=CompanyId(uuid4()),
                name=request.name,
                description=request.description,
                owner=user,
            )

            logger.info("Created company", company_id=company.id)

            await self.company_repository.create(company)

            return company
