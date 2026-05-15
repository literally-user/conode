from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from prodik.domain.company import CompanyId


class CreateContextRequest(BaseModel):
    name: str
    description: str
    company_id: CompanyId


class CreateContextRequestFactory(ModelFactory[CreateContextRequest]):
    __model__ = CreateContextRequest
