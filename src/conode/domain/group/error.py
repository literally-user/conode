from conode.application.errors import ApplicationError


class GroupDomainValidationError(ApplicationError): ...


class InvalidGroupNameFormatError(ApplicationError): ...


class InvalidGroupDescriptionFormatError(ApplicationError): ...
