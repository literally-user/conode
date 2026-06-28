from polyfactory.factories.pydantic_factory import ModelFactory

from prodik.presentation.schemas.node import CreateNodeRequest, UpdateNodeRequest


class CreateNodeRequestFactory(ModelFactory[CreateNodeRequest]):
    __use_examples__ = True


class UpdateNodeRequestFactory(ModelFactory[UpdateNodeRequest]):
    __use_examples__ = True
