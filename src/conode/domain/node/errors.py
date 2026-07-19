from conode.application.errors import ApplicationError


class NodeDomainValidationError(ApplicationError): ...


class InvalidNodeNameFormatError(NodeDomainValidationError): ...


class InvalidNodeDescriptionFormatError(NodeDomainValidationError): ...
