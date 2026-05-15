from typing import Any, ClassVar, override

from sqlalchemy import Dialect, String
from sqlalchemy.types import TypeDecorator

from prodik.domain.company import CompanyDescription, CompanyName
from prodik.domain.context import ContextDescription, ContextName
from prodik.domain.group import GroupDescription, GroupName
from prodik.domain.node import NodeDescription, NodeName
from prodik.domain.offer import OfferDescription, OfferTitle
from prodik.domain.role import RoleName
from prodik.domain.shared import ValueObject
from prodik.domain.user import Bio, Email, FirstName, LastName, Username


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


class LastNameType(BaseVOTypeDecorator[LastName]):
    impl = String
    cache_ok = True
    vo_class = LastName


class FirstNameType(BaseVOTypeDecorator[FirstName]):
    impl = String
    cache_ok = True
    vo_class = FirstName


class EmailType(BaseVOTypeDecorator[Email]):
    impl = String
    cache_ok = True
    vo_class = Email


class BioType(BaseVOTypeDecorator[Bio]):
    impl = String
    cache_ok = True
    vo_class = Bio


class CompanyNameType(BaseVOTypeDecorator[CompanyName]):
    impl = String
    cache_ok = True
    vo_class = CompanyName


class CompanyDescriptionType(BaseVOTypeDecorator[CompanyDescription]):
    impl = String
    cache_ok = True
    vo_class = CompanyDescription


class NodeDescriptionType(BaseVOTypeDecorator[NodeDescription]):
    impl = String
    cache_ok = True
    vo_class = NodeDescription


class NodeNameType(BaseVOTypeDecorator[NodeName]):
    impl = String
    cache_ok = True
    vo_class = NodeName


class GroupDescriptionType(BaseVOTypeDecorator[GroupDescription]):
    impl = String
    cache_ok = True
    vo_class = GroupDescription


class GroupNameType(BaseVOTypeDecorator[GroupName]):
    impl = String
    cache_ok = True
    vo_class = GroupName


class ContextNameType(BaseVOTypeDecorator[ContextName]):
    impl = String
    cache_ok = True
    vo_class = ContextName


class ContextDescriptionType(BaseVOTypeDecorator[ContextDescription]):
    impl = String
    cache_ok = True
    vo_class = ContextDescription


class RoleNameType(BaseVOTypeDecorator[RoleName]):
    impl = String
    cache_ok = True
    vo_class = RoleName


class OfferTitleType(BaseVOTypeDecorator[OfferTitle]):
    impl = String
    cache_ok = True
    vo_class = OfferTitle


class OfferDescriptionType(BaseVOTypeDecorator[OfferDescription]):
    impl = String
    cache_ok = True
    vo_class = OfferDescription
