from conode.application.errors import ApplicationError


class RoleDomainValidationError(ApplicationError): ...


class InvalidRoleNameFormatError(RoleDomainValidationError): ...
