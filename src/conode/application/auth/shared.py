from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthorizedResponseDTO:
    access_token: str
    refresh_token: str
    expires_in: int
