import jwt

from conode.application.interfaces.token_manager import (
    TokenManager,
    UserMeta,
)
from conode.domain.user import UserSystemRole
from conode.domain.user.model import User
from conode.infrastructure.config import SecretsConfig


class TokenManagerImpl(TokenManager):
    def __init__(self, config: SecretsConfig) -> None:
        self._client = jwt.PyJWKClient(config.jwks_url)
        self._config = config

    def encode(self, user: User) -> str:
        raise NotImplementedError

    def decode(self, token: str) -> UserMeta:
        signing_key = self._client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self._config.audience,
            issuer=self._config.issuer,
        )
        role = UserSystemRole.USER
        if "realm-admin" in payload["resource_access"]["realm-management"]["roles"]:
            role = UserSystemRole.ADMIN

        return UserMeta(
            email=payload["email"],
            first_name=payload["given_name"],
            last_name=payload["family_name"],
            username=payload["preferred_username"],
            system_role=role,
        )
