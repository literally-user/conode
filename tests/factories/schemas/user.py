from polyfactory.factories.pydantic_factory import ModelFactory

from prodik.presentation.schemas.user import (
    UpdateCurrentUserPasswordRequest,
    UpdateCurrentUserProfileRequest,
)


class UpdateCurrentUserPasswordRequestFactory(
    ModelFactory[UpdateCurrentUserPasswordRequest]
): ...


class UpdateCurrentUserProfileRequestFactory(
    ModelFactory[UpdateCurrentUserProfileRequest]
): ...
