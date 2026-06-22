from polyfactory.factories.pydantic_factory import ModelFactory

from prodik.presentation.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
)


class RegisterRequestFactory(ModelFactory[RegisterRequest]):
    __use_examples__ = True


class RefreshTokenRequestFactory(ModelFactory[RefreshTokenRequest]): ...


class LoginRequestFactory(ModelFactory[LoginRequest]): ...
