from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from prodik.domain.context import ContextId
from prodik.domain.node import NodeId


class CreateEdgeRequest(BaseModel):
    node_a_id: NodeId
    node_b_id: NodeId
    context_id: ContextId


class UpdateEdgeWeightRequest(BaseModel):
    weight: float


class CreateEdgeRequestFactory(ModelFactory[CreateEdgeRequest]):
    __model__ = CreateEdgeRequest


class UpdateEdgeWeightRequestFactory(ModelFactory[UpdateEdgeWeightRequest]):
    __model__ = UpdateEdgeWeightRequest
