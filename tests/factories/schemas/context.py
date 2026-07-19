from polyfactory.factories.pydantic_factory import ModelFactory

from conode.presentation.schemas.context import CreateContextRequest


class CreateContextRequestFactory(ModelFactory[CreateContextRequest]):
    __use_examples__ = True
