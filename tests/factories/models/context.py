from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.repositories import ContextRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.company import Company
from prodik.domain.context import Context, ContextId
from tests.factories.common import generate_random_string


@dataclass
class ContextFactory:
    transaction_manager: TransactionManager
    context_repository: ContextRepository

    async def build(self, *, company: Company) -> Context:
        async with self.transaction_manager:
            context = Context.new(
                context_id=ContextId(uuid4()),
                name=generate_random_string(),
                description=generate_random_string(),
                company=company,
            )

            await self.context_repository.create(context)

            return context
