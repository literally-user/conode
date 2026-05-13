from typing import Annotated

from pydantic import BaseModel, Field

from prodik.domain.company import CompanyId
from prodik.domain.context import ContextId
from prodik.domain.context.model import (
    MAX_ALLOWED_CONTEXT_DESCRIPTION_LENGTH,
    MAX_ALLOWED_CONTEXT_NAME_LENGTH,
    MIN_ALLOWED_CONTEXT_NAME_LENGTH,
)


class CreateContextRequest(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_CONTEXT_NAME_LENGTH,
            max_length=MAX_ALLOWED_CONTEXT_NAME_LENGTH,
        ),
    ]
    description: Annotated[
        str,
        Field(max_length=MAX_ALLOWED_CONTEXT_DESCRIPTION_LENGTH),
    ]
    company_id: CompanyId


class ContextSchema(BaseModel):
    id: ContextId
    name: str
    description: str
    company_id: CompanyId
