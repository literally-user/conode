from polyfactory.factories.pydantic_factory import ModelFactory

from prodik.presentation.schemas.company import RegisterCompanyRequest


class RegisterCompanyRequestFactory(ModelFactory[RegisterCompanyRequest]):
    __use_examples__ = True
