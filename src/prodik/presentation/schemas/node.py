from typing import Annotated

from pydantic import BaseModel, Field

from prodik.domain.company import CompanyId
from prodik.domain.group import GroupId
from prodik.domain.node import NodeAssociationId, NodeId


class CreateNodeRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]
    description: Annotated[str, Field(max_length=300)]
    group_id: GroupId


class NodeSchema(BaseModel):
    id: NodeId
    name: str
    description: str
    company_id: CompanyId


class AttachNodeRequest(BaseModel):
    group_id: GroupId
    nodes: list[NodeId]


class NodeAssociationSchema(BaseModel):
    id: NodeAssociationId
    node_id: NodeId
    group_id: GroupId
