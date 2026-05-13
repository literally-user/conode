from typing import Any, TypedDict


class ApplicationErrorMeta(TypedDict):
    key: str
    value: Any


class ApplicationError(Exception):
    def __init__(self, detail: str, meta: list[ApplicationErrorMeta] | None) -> None:
        self.detail = detail
        self.meta = meta
        super().__init__(detail)


class UserAlreadyExistsError(ApplicationError): ...


class FailedToReadClientError(ApplicationError): ...


class InvalidTokenError(ApplicationError): ...


class SessionExpiredError(ApplicationError): ...


class SessionNotFoundError(ApplicationError): ...


class AuthorizationNotFoundError(ApplicationError): ...


class InvalidCredentialsError(ApplicationError): ...


class UserNotFoundError(ApplicationError): ...


class InvalidOldPasswordError(ApplicationError): ...


class CompanyAlreadyExistsError(ApplicationError): ...


class NotEnoughRightsError(ApplicationError): ...


class CompanyNotFoundError(ApplicationError): ...


class GroupNotFoundError(ApplicationError): ...


class AssociationNotFoundError(ApplicationError): ...


class NodeNotFoundError(ApplicationError): ...


class ContextNotFoundError(ApplicationError): ...


class EdgeNotFoundError(ApplicationError): ...


class EdgeAlreadyExistsError(ApplicationError): ...


class NodeCannotHaveSameAssociationsError(ApplicationError): ...


class NodeMustHaveAtLeastOneAssociationError(ApplicationError): ...


class RoleAlreadyExistsError(ApplicationError): ...


class RoleNotFoundError(ApplicationError): ...


class GrantNotFoundError(ApplicationError): ...


class GrantAlreadyExistsError(ApplicationError): ...
