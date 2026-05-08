from typing import Annotated

from pydantic import BaseModel, Field

from prodik.domain.company import CompanyId
from prodik.domain.user import UserId


class CompanySchema(BaseModel):
    id: CompanyId
    name: str
    owner_id: UserId
    description: str
    verified: bool


class RegisterCompanyRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]
    description: Annotated[str, Field(min_length=20, max_length=3000)]
