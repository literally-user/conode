from dataclasses import dataclass
from datetime import timedelta
from uuid import uuid4

from conode.application.interfaces.password_hasher import PasswordHasher
from conode.application.interfaces.repositories import (
    AuthorizationRepository,
    SessionRepository,
    UserRepository,
)
from conode.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.application.services import AuthorizationService
from conode.domain.user import User, UserId, UserSystemRole
from tests.factories.common import generate_random_string


@dataclass
class UserFactoryResponse:
    user: User
    access_token: str
    refresh_token: str
    password: str


@dataclass
class UserFactory:
    authorization_repository: AuthorizationRepository
    session_repository: SessionRepository
    authorization_service: AuthorizationService
    refresh_token_manager: RefreshTokenManager
    access_token_manager: AccessTokenManager
    transaction_manager: TransactionManager
    user_repository: UserRepository
    password_hasher: PasswordHasher

    def generate_access_token(self, user: User) -> str:
        return self.access_token_manager.encode(user).token

    async def build(
        self,
        *,
        admin: bool = False,
        verified: bool = True,
        timedelta_ago: timedelta | None = None,
    ) -> UserFactoryResponse:
        async with self.transaction_manager:
            user = User.new(
                user_id=UserId(uuid4()),
                first_name=generate_random_string(),
                last_name=generate_random_string(),
                username=generate_random_string(
                    include_digits=False, include_special_symbols=False
                ),
                email=generate_random_string(
                    include_digits=False,
                    include_special_symbols=False,
                    include_uppercase=False,
                )
                + "@testing.org",
                bio=generate_random_string(100),
            )
            if admin:
                user.system_role = UserSystemRole.ADMIN
            if timedelta_ago is not None:
                user.created_at -= timedelta_ago

            user.email_verified = verified

            password = generate_random_string(15)
            authorization_service_response = (
                self.authorization_service.generate_authorization_stuff(
                    user,
                    password,
                    "127.0.0.1",
                )
            )

            await self.user_repository.create(user)
            await self.authorization_repository.create(
                authorization_service_response.authorization
            )
            await self.session_repository.create(authorization_service_response.session)

            return UserFactoryResponse(
                user=user,
                access_token=authorization_service_response.access_token,
                refresh_token=authorization_service_response.refresh_token,
                password=password,
            )
