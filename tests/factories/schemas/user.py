from polyfactory.factories.pydantic_factory import ModelFactory

from conode.presentation.schemas.user import (
    UpdateCurrentUserProfileRequest,
)


class UpdateCurrentUserProfileRequestFactory(
    ModelFactory[UpdateCurrentUserProfileRequest]
): ...
