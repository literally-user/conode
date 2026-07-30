from polyfactory.factories.pydantic_factory import ModelFactory

from conode.presentation.schemas.company import RegisterCompanyRequest


class RegisterCompanyRequestFactory(ModelFactory[RegisterCompanyRequest]):
    __use_examples__ = True
