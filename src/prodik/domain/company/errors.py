from prodik.application.errors import ApplicationError


class CompanyDomainValidationError(ApplicationError): ...


class InvalidCompanyNameFormatError(CompanyDomainValidationError): ...


class InvalidCompanyDescriptionFormatError(CompanyDomainValidationError): ...
