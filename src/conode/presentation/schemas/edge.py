from pydantic import BaseModel

from conode.domain.company import CompanyId
from conode.domain.context import ContextId
from conode.domain.edge import EdgeId
from conode.domain.node import NodeId


class CreateEdgeRequest(BaseModel):
    node_a_id: NodeId
    node_b_id: NodeId
    context_id: ContextId


class UpdateEdgeWeightRequest(BaseModel):
    weight: float


class EdgeSchema(BaseModel):
    id: EdgeId
    node_a_id: NodeId
    node_b_id: NodeId
    context_id: ContextId
    company_id: CompanyId
