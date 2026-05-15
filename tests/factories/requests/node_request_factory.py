from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from prodik.domain.group import GroupId
from prodik.domain.node import NodeId


class CreateNodeRequest(BaseModel):
    name: str
    description: str
    group_id: GroupId


class UpdateNodeRequest(BaseModel):
    name: str
    description: str


class AttachNodeRequest(BaseModel):
    group_id: GroupId
    nodes: list[NodeId]


class CreateNodeRequestFactory(ModelFactory[CreateNodeRequest]):
    __model__ = CreateNodeRequest


class UpdateNodeRequestFactory(ModelFactory[UpdateNodeRequest]):
    __model__ = UpdateNodeRequest


class AttachNodeRequestFactory(ModelFactory[AttachNodeRequest]):
    __model__ = AttachNodeRequest
