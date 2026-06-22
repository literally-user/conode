from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.application.interfaces.repositories import (
    LocalAuthorizationRepository,
    SessionRepository,
    UserRepository,
)
from prodik.application.interfaces.token_managers import (
    AccessTokenManager,
    RefreshTokenManager,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.authorization import (
    LocalAuthorization,
    LocalAuthorizationId,
    Session,
    SessionId,
)
from prodik.domain.user import User, UserId
from tests.factories.common import generate_random_ip, generate_random_string


@dataclass
class UserFactoryResponse:
    user: User
    access_token: str
    refresh_token: str
    password: str


@dataclass
class UserFactory:
    local_authorization_repository: LocalAuthorizationRepository
    refresh_token_manager: RefreshTokenManager
    access_token_manager: AccessTokenManager
    transaction_manager: TransactionManager
    session_repository: SessionRepository
    user_repository: UserRepository
    password_hasher: PasswordHasher

    async def build(self) -> UserFactoryResponse:
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

            access_token = self.access_token_manager.encode(user)
            refresh_token = self.refresh_token_manager.encode()
            password = generate_random_string()
            hashed_password = self.password_hasher.hash(password)

            authorization = LocalAuthorization.new(
                local_authorization_id=LocalAuthorizationId(uuid4()),
                password=hashed_password,
                user=user,
            )

            session = Session.new(
                session_id=SessionId(uuid4()),
                host=generate_random_ip(),
                token=refresh_token,
                user=user,
            )

            await self.user_repository.create(user)
            await self.local_authorization_repository.create(authorization)
            await self.session_repository.create(session)

            return UserFactoryResponse(
                user=user,
                access_token=access_token.token,
                refresh_token=refresh_token,
                password=password,
            )
