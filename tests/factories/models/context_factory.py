from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.repositories import ContextRepository
from prodik.domain.company import Company
from prodik.domain.context import Context, ContextId
from tests.factories.common import generate_random_string
from tests.factories.models.company_factory import CompanyFactory


@dataclass(slots=True)
class ContextFactory:
    context_repository: ContextRepository
    company_factory: CompanyFactory

    async def create_context(self, company: Company | None = None) -> Context:
        context = Context.new(
            context_id=ContextId(uuid4()),
            name=generate_random_string(10),
            description=generate_random_string(30),
            company=company or await self.company_factory.create_company(),
        )

        await self.context_repository.create(context)

        return context
