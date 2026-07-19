from typing import Annotated

from pydantic import BaseModel, Field

from conode.domain.company import CompanyId
from conode.domain.group import GroupId
from conode.domain.node import NodeAssociationId, NodeId
from conode.domain.node.model import (
    MAX_ALLOWED_NODE_DESCRIPTION_LENGTH,
    MAX_ALLOWED_NODE_NAME_LENGTH,
    MIN_ALLOWED_NODE_NAME_LENGTH,
)


class CreateNodeRequest(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_NODE_NAME_LENGTH,
            max_length=MAX_ALLOWED_NODE_NAME_LENGTH,
        ),
    ]
    description: Annotated[
        str,
        Field(max_length=MAX_ALLOWED_NODE_DESCRIPTION_LENGTH),
    ]
    group_id: GroupId


class UpdateNodeRequest(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_NODE_NAME_LENGTH,
            max_length=MAX_ALLOWED_NODE_NAME_LENGTH,
        ),
    ]
    description: Annotated[
        str,
        Field(max_length=MAX_ALLOWED_NODE_DESCRIPTION_LENGTH),
    ]


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
