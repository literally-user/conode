from dataclasses import dataclass
from typing import Final

from fastapi import Request
from jwt.exceptions import PyJWTError

from prodik.application.errors import FailedToReadClientError, InvalidTokenError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.token_managers import AccessTokenManager
from prodik.domain.user import UserId

TOKEN_TYPE: Final = "Bearer"  # noqa: S105
TOKEN_SECTIONS: Final = 2


@dataclass
class IdentityProviderImpl(IdentityProvider):
    request: Request
    access_token_manager: AccessTokenManager

    def get_current_ip(self) -> str:
        if self.request.client is None:
            raise FailedToReadClientError("Failed to read client error", None)

        return self.request.client.host

    def get_current_user_id(self) -> UserId:
        header = self.request.headers.get("Authorization")
        if header is None:
            raise InvalidTokenError("Authorization token not found", None)

        header_content = header.split(" ")
        if len(header_content) != TOKEN_SECTIONS:
            raise InvalidTokenError(
                "Invalid authorization token format",
                [{"key": "Authorization", "value": header}],
            )

        token_type, token = header_content
        if token_type != TOKEN_TYPE:
            raise InvalidTokenError(
                "Invalid authorization token type",
                [{"key": "Authorization", "value": token_type}],
            )

        try:
            content = self.access_token_manager.decode(token)
        except PyJWTError as e:
            raise InvalidTokenError(
                "Invalid authorization token",
                [{"key": "Authorization", "value": token}],
            ) from e

        return content["user_id"]
