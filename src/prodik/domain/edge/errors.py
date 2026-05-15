from prodik.application.errors import ApplicationError


class EdgeDomainValidationError(ApplicationError): ...


class EdgeCannotConnectTwoSameNodesError(EdgeDomainValidationError): ...
