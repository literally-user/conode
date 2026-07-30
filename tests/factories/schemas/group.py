from polyfactory.factories.pydantic_factory import ModelFactory

from conode.presentation.schemas.group import CreateGroupRequest


class CreateGroupRequestFactory(ModelFactory[CreateGroupRequest]):
    __use_examples__ = True
