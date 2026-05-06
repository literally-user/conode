from typing import Any, ClassVar, override

from sqlalchemy import Dialect, String
from sqlalchemy.types import TypeDecorator

from conode.domain.company import CompanyDescription, CompanyName
from conode.domain.shared import ValueObject
from conode.domain.user import Email, FirstName, LastName, Username


class BaseVOTypeDecorator[T: ValueObject[Any]](TypeDecorator[T]):
    vo_class: ClassVar[type]

    @override
    def process_bind_param(self, value: T | None, dialect: Dialect) -> Any:
        if value is None:
            return None

        return value.value

    @override
    def process_result_value(self, value: Any | None, dialect: Dialect) -> T | None:
        return self.vo_class(value) if value else None


class UsernameType(BaseVOTypeDecorator[Username]):
    impl = String
    cache_ok = True
    vo_class = Username


class FirstNameType(BaseVOTypeDecorator[FirstName]):
    impl = String
    cache_ok = True
    vo_class = FirstName


class LastNameType(BaseVOTypeDecorator[LastName]):
    impl = String
    cache_ok = True
    vo_class = LastName


class EmailType(BaseVOTypeDecorator[Email]):
    impl = String
    cache_ok = True
    vo_class = Email


class CompanyNameType(BaseVOTypeDecorator[CompanyName]):
    impl = String
    cache_ok = True
    vo_class = CompanyName


class CompanyDescriptionType(BaseVOTypeDecorator[CompanyDescription]):
    impl = String
    cache_ok = True
    vo_class = CompanyDescription
