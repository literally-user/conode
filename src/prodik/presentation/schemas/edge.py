from datetime import datetime

from pydantic import BaseModel

from prodik.domain.company import CompanyId
from prodik.domain.context import ContextId
from prodik.domain.edge import EdgeId
from prodik.domain.node import NodeId


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
    created_at: datetime
    updated_at: datetime
