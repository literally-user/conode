from typing import Any, TypedDict


class ApplicationErrorMeta(TypedDict):
    key: str
    value: Any


class ApplicationError(Exception):
    def __init__(
        self, detail: str, meta: list[ApplicationErrorMeta] | None = None
    ) -> None:
        self.detail = detail
        self.meta = meta
        super().__init__(detail)


class UserAlreadyExistsError(ApplicationError): ...
