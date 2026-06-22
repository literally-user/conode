from polyfactory.factories.pydantic_factory import ModelFactory

from prodik.presentation.schemas.auth import RegisterRequest


class RegisterRequestFactory(ModelFactory[RegisterRequest]):
    __use_examples__ = True
