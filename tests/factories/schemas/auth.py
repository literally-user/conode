from polyfactory.factories.pydantic_factory import ModelFactory

from conode.presentation.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
)


class RegisterRequestFactory(ModelFactory[RegisterRequest]):
    __use_examples__ = True


class LoginRequestFactory(ModelFactory[LoginRequest]): ...


class RefreshTokenRequestFactory(ModelFactory[RefreshTokenRequest]): ...
