from dataclasses import dataclass
from uuid import uuid4

from conode.application.interfaces.password_hasher import PasswordHasher
from conode.application.interfaces.repositories import UserRepository
from conode.application.interfaces.token_manager import TokenManager
from conode.application.interfaces.transaction_manager import TransactionManager
from conode.domain.user import User, UserId, UserSystemRole
from tests.factories.common import generate_random_string


@dataclass
class UserFactoryResponse:
    user: User
    access_token: str


@dataclass
class UserFactory:
    token_manager: TokenManager
    transaction_manager: TransactionManager
    user_repository: UserRepository
    password_hasher: PasswordHasher

    def generate_access_token(self, user: User) -> str:
        return self.token_manager.encode(user)

    async def build(self, *, admin: bool = False) -> UserFactoryResponse:
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

            await self.user_repository.create(user)

            return UserFactoryResponse(
                user=user,
                access_token=self.generate_access_token(user),
            )
