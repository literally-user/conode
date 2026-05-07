import random
from dataclasses import dataclass
from typing import Annotated
from uuid import uuid4

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, EmailStr, Field

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


class RegisterRequest(BaseModel):
    username: Annotated[str, Field(min_length=5, max_length=30)]
    first_name: Annotated[str, Field(min_length=1, max_length=30)]
    last_name: Annotated[str, Field(min_length=1, max_length=30)]
    password: Annotated[str, Field(min_length=7, max_length=100)]
    email: EmailStr


class RegisterRequestFactory(ModelFactory[RegisterRequest]):
    __model__ = RegisterRequest


@dataclass
class UserFactoryResponse:
    user: User
    session: Session
    authorization: LocalAuthorization
    access_token: str
    refresh_token: str
    password: str


@dataclass
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
        await self.session_repository.create(session)
        await self.authorization_repository.create(authorization)

        return UserFactoryResponse(
            user=user,
            session=session,
            authorization=authorization,
            access_token=access_token,
            refresh_token=refresh_token,
            password=password,
        )


def generate_random_string(length: int = 5) -> str:
    return "".join(
        [random.choice(list("qwertyuiopasdfghjklzxcvbnm")) for _ in range(length)]  # noqa: S311
    )
