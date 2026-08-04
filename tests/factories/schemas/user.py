from polyfactory.factories.pydantic_factory import ModelFactory

from conode.presentation.schemas.user import (
    UpdateCurrentUserProfileRequest,
    UpdateUserProfileRequest,
)


class UpdateCurrentUserProfileRequestFactory(
    ModelFactory[UpdateCurrentUserProfileRequest]
): ...


class UpdateUserProfileRequestFactory(ModelFactory[UpdateUserProfileRequest]): ...
