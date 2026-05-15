from prodik.application.errors import ApplicationError


class ContextDomainValidationError(ApplicationError): ...


class InvalidContextDescriptionFormatError(ContextDomainValidationError): ...


class InvalidContextNameFormatError(ContextDomainValidationError): ...
