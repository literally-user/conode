from dataclasses import dataclass
from typing import Final

from fastapi import Request

from prodik.application.authorization.errors import (
    InvalidAccessHeaderError,
    InvalidClientError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.token_managers import AccessTokenManager
from prodik.domain.user import UserId

HEADER_NAME: Final = "Authorization"
TOKEN_TYPE: Final = "Bearer"  # noqa: S105
TOKEN_SECTIONS: Final = 2


@dataclass
class IdentityProviderImpl(IdentityProvider):
    _request: Request
    access_token_manager: AccessTokenManager

    def get_current_user_id(self) -> UserId:
        header = self._request.headers.get(HEADER_NAME)
        if header is None:
            raise InvalidAccessHeaderError("Token not found", None)

        header_content = header.split(" ")
        if len(header_content) != TOKEN_SECTIONS:
            raise InvalidAccessHeaderError("Invalid token format", None)

        token_type, token = header_content
        if token_type != TOKEN_TYPE:
            raise InvalidAccessHeaderError("Invalid token type", None)

        token_content = self.access_token_manager.decode(token)

        return token_content["user_id"]

    def get_current_ip(self) -> str:
        client = self._request.client
        if client is None:
            raise InvalidClientError("Failed to parse client", None)

        return client.host
