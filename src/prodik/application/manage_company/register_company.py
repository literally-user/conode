from dataclasses import dataclass
from uuid import uuid4

import structlog

from prodik.application.errors import CompanyAlreadyExistsError
from prodik.application.interfaces.repositories import CompanyRepository
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
    company_repository: CompanyRepository
    transaction_manager: TransactionManager
    access_control_service: AccessControlService

    async def execute(self, request: RegisterCompanyRequestDTO) -> Company:
        async with self.transaction_manager:
            user = await self.access_control_service.get_authorized_user()

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
