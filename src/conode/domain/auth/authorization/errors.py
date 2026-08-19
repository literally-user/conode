from conode.application.errors import ApplicationError


class AuthorizationDomainValidationError(ApplicationError): ...


class InvalidAuthorizationPasswordFormatError(AuthorizationDomainValidationError): ...
