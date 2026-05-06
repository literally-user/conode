from prodik.application.errors import ApplicationError


class ContractDomainValidationError(ApplicationError): ...


class InvalidCompanyOffersFormatError(ContractDomainValidationError): ...
