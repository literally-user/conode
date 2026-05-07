from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class UpdateCurrentUserProfileRequest(BaseModel):
    username: Annotated[str, Field(min_length=5, max_length=30)]
    first_name: Annotated[str, Field(min_length=1, max_length=30)]
    last_name: Annotated[str, Field(min_length=1, max_length=30)]
    password: Annotated[str, Field(min_length=7, max_length=100)]
    email: EmailStr
    bio: str
