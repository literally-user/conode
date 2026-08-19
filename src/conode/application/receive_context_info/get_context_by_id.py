from dataclasses import dataclass

from conode.application.interfaces.repositories import ContextRepository
from conode.application.services import AccessControlService, AuthorizationService
from conode.domain.context import Context, ContextId


@dataclass
class GetContextByIdInteractor:
    access_control_service: AccessControlService
    authorization_service: AuthorizationService
    context_repository: ContextRepository

    async def execute(self, context_id: ContextId) -> Context:
        user = await self.authorization_service.get_authorized_user()

        context = await self.context_repository.get_by_id(context_id)

        await self.access_control_service.ensure_user_can_view_context(
            user,
            context,
        )

        return context
