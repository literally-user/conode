from polyfactory.factories.pydantic_factory import ModelFactory

from prodik.presentation.schemas.node import CreateNodeRequest


class CreateNodeRequestFactory(ModelFactory[CreateNodeRequest]):
    __use_examples__ = True
