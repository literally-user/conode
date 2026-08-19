from dataclasses import dataclass
from typing import Final

import structlog
from fastapi import Request
from jwt import PyJWTError

from conode.application.errors import FailedToReadClientError, InvalidTokenError
from conode.application.interfaces.identity_provider import IdentityProvider
from conode.application.interfaces.token_managers import AccessTokenManager, UserMeta

logger = structlog.get_logger()

AUTHORIZATION_HEADER_NAME: Final = "Authorization"


@dataclass
class IdentityProviderImpl(IdentityProvider):
    request: Request
    access_token_manager: AccessTokenManager

    def get_current_ip(self) -> str:
        if self.request.client is None:
            raise FailedToReadClientError("Failed to read client error", None)

        return self.request.client.host

    def get_current_user_meta(self) -> UserMeta:
        token = self.request.headers.get(AUTHORIZATION_HEADER_NAME)
        if token is None:
            raise InvalidTokenError("Authorization token not found", None)

        try:
            content = self.access_token_manager.decode(token)
        except PyJWTError as e:
            raise InvalidTokenError(
                "Invalid authorization token",
                [{"key": AUTHORIZATION_HEADER_NAME, "value": token}],
            ) from e

        return content
