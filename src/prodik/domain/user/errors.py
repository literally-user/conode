from prodik.application.errors import ApplicationError


class UserDomainValidationError(ApplicationError): ...


class UsernameCannotBeShorterThanError(UserDomainValidationError): ...


class UsernameCannotBeLongerThanError(UserDomainValidationError): ...
