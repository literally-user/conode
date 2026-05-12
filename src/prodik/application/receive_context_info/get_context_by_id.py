from dataclasses import dataclass

from prodik.application.errors import ContextNotFoundError
from prodik.application.interfaces.repositories import ContextRepository
from prodik.application.services import AccessControlService
from prodik.domain.context import Context, ContextId


@dataclass
class GetContextByIdInteractor:
    access_control_service: AccessControlService
    context_repository: ContextRepository

    async def execute(self, context_id: ContextId) -> Context:
        user = await self.access_control_service.get_authorized_user()

        context = await self.context_repository.get_by_id(context_id)
        if context is None:
            raise ContextNotFoundError("Context not found", None)

        await self.access_control_service.ensure_user_can_view_context(
            user,
            context,
        )

        return context
