from typing import Annotated

from pydantic import BaseModel, Field

from prodik.domain.company import CompanyId
from prodik.domain.group import GroupId
from prodik.domain.node import NodeId


class CreateNodeRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]
    description: Annotated[str, Field(max_length=300)]
    group_id: GroupId


class NodeSchema(BaseModel):
    id: NodeId
    name: str
    description: str
    company_id: CompanyId
