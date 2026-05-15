import asyncio
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
from prodik.domain.authorization import (
    LocalAuthorization,
    LocalAuthorizationId,
    Session,
    SessionId,
)
from prodik.domain.user import User, UserId, UserSystemRole
from tests.factories.common import generate_random_string


@dataclass
class UserFactoryResponse:
    user: User
    session: Session
    authorization: LocalAuthorization
    access_token: str
    refresh_token: str
    password: str


@dataclass(slots=True)
class UserFactory:
    password_hasher: PasswordHasher
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager
    user_repository: UserRepository
    session_repository: SessionRepository
    authorization_repository: LocalAuthorizationRepository

    async def create_user(self, *, admin: bool = False) -> UserFactoryResponse:
        user = User.new(
            id=UserId(uuid4()),
            username=generate_random_string(10),
            first_name=generate_random_string(10),
            last_name=generate_random_string(10),
            email=generate_random_string(10) + "@conode.team",
            bio=generate_random_string(100),
        )

        if admin:
            user.system_role = UserSystemRole.ADMIN

        password = generate_random_string(10)
        hashed_password = self.password_hasher.hash(password)
        access_token, _ = self.access_token_manager.encode(user)
        refresh_token = self.refresh_token_manager.encode()

        authorization = LocalAuthorization.new(
            id=LocalAuthorizationId(uuid4()),
            password=hashed_password,
            user=user,
        )

        session = Session.new(
            id=SessionId(uuid4()),
            user=user,
            host="127.0.0.1",
            token=refresh_token,
        )

        await self.user_repository.create(user)
        await asyncio.gather(
            self.session_repository.create(session),
            self.authorization_repository.create(authorization),
        )

        return UserFactoryResponse(
            user=user,
            session=session,
            authorization=authorization,
            access_token=access_token,
            refresh_token=refresh_token,
            password=password,
        )
