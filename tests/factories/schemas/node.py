from polyfactory.factories.pydantic_factory import ModelFactory

from conode.presentation.schemas.node import (
    AttachNodeRequest,
    CreateNodeRequest,
    UpdateNodeRequest,
)


class CreateNodeRequestFactory(ModelFactory[CreateNodeRequest]):
    __use_examples__ = True


class UpdateNodeRequestFactory(ModelFactory[UpdateNodeRequest]):
    __use_examples__ = True


class AttachNodeRequestFactory(ModelFactory[AttachNodeRequest]):
    __use_examples__ = True
