from typing import Protocol

from prodik.domain.authorization import OAuthAuthorization


class OAuthAuthorizationRepository(Protocol):
    async def create(self, authorization: OAuthAuthorization) -> None: ...
