from polyfactory.factories.pydantic_factory import ModelFactory

from conode.presentation.schemas.company import (
    RegisterCompanyRequest,
    TransferCompanyRequest,
    UpdateCompanyRequest,
)


class RegisterCompanyRequestFactory(ModelFactory[RegisterCompanyRequest]):
    __use_examples__ = True


class UpdateCompanyRequestFactory(ModelFactory[UpdateCompanyRequest]):
    __use_examples__ = True


class TransferCompanyRequestFactory(ModelFactory[TransferCompanyRequest]): ...
