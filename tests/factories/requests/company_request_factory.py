from typing import Annotated

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field


class RegisterCompanyRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]
    description: Annotated[str, Field(min_length=20, max_length=3000)]


class RegisterCompanyRequestFactory(ModelFactory[RegisterCompanyRequest]):
    __model__ = RegisterCompanyRequest
