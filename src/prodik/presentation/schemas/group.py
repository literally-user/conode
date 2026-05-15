from typing import Annotated

from pydantic import BaseModel, Field

from prodik.domain.company import CompanyId
from prodik.domain.group import GroupId
from prodik.domain.group.model import (
    MAX_ALLOWED_GROUP_DESCRIPTION_LENGTH,
    MAX_ALLOWED_GROUP_NAME_LENGTH,
    MIN_ALLOWED_GROUP_NAME_LENGTH,
)


class CreateGroupRequest(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_GROUP_NAME_LENGTH,
            max_length=MAX_ALLOWED_GROUP_NAME_LENGTH,
        ),
    ]
    description: Annotated[
        str,
        Field(max_length=MAX_ALLOWED_GROUP_DESCRIPTION_LENGTH),
    ]
    parent_group_id: GroupId | None = None
    company_id: CompanyId


class GroupSchema(BaseModel):
    id: GroupId
    name: str
    description: str
    company_id: CompanyId
    parent_group_id: GroupId | None
