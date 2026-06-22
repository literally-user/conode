from polyfactory.factories.pydantic_factory import ModelFactory

from prodik.presentation.schemas.auth import LoginRequest, RegisterRequest


class RegisterRequestFactory(ModelFactory[RegisterRequest]):
    __use_examples__ = True


class LoginRequestFactory(ModelFactory[LoginRequest]): ...
