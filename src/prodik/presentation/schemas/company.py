from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from prodik.domain.company import CompanyId
from prodik.domain.company.model import (
    MAX_ALLOWED_COMPANY_DESCRIPTION_LENGTH,
    MAX_ALLOWED_COMPANY_NAME_LENGTH,
    MIN_ALLOWED_COMPANY_DESCRIPTION_LENGTH,
    MIN_ALLOWED_COMPANY_NAME_LENGTH,
)
from prodik.domain.user import UserId


class CompanySchema(BaseModel):
    id: CompanyId
    name: str
    owner_id: UserId
    description: str
    verified: bool
    created_at: datetime
    updated_at: datetime


class RegisterCompanyRequest(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_COMPANY_NAME_LENGTH,
            max_length=MAX_ALLOWED_COMPANY_NAME_LENGTH,
        ),
    ]
    description: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_COMPANY_DESCRIPTION_LENGTH,
            max_length=MAX_ALLOWED_COMPANY_DESCRIPTION_LENGTH,
        ),
    ]
