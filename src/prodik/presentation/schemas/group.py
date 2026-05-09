from typing import Annotated

from pydantic import BaseModel, Field

from prodik.domain.company import CompanyId
from prodik.domain.group import GroupId


class CreateGroupRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]
    description: Annotated[str, Field(max_length=300)]
    parent_group_id: GroupId | None = None


class GroupSchema(BaseModel):
    id: GroupId
    name: str
    description: str
    company_id: CompanyId
    parent_group_id: GroupId | None
