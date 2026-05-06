from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class RegisterRequest(BaseModel):
    username: Annotated[str, Field(min_length=5, max_length=30)]
    first_name: Annotated[str, Field(min_length=1, max_length=30)]
    last_name: Annotated[str, Field(min_length=1, max_length=30)]
    password: Annotated[str, Field(min_length=5, max_length=300)]
    email: EmailStr
