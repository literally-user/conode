from dishka import Provider, Scope, provide_all

from prodik.application.authorization import (
    LoginInteractor,
    RefreshTokenInteractor,
    RegisterInteractor,
)
from prodik.application.manage_association import (
    AttachNodeInteractor,
    DetachNodeInteractor,
)
from prodik.application.manage_company import (
    RegisterCompanyInteractor,
    VerifyCompanyInteractor,
)
from prodik.application.manage_contexts import (
    CreateContextInteractor,
    DeleteContextInteractor,
)
from prodik.application.manage_credentials import UpdateCurrentUserPasswordInteractor
from prodik.application.manage_edges import (
    CreateEdgeInteractor,
    DecrementEdgeWeightInteractor,
    DeleteEdgeInteractor,
    IncrementEdgeWeightInteractor,
    UpdateEdgeWeightInteractor,
)
from prodik.application.manage_group import CreateGroupInteractor, DeleteGroupInteractor
from prodik.application.manage_node import (
    CreateNodeInteractor,
    DeleteNodeInteractor,
    UpdateNodeInteractor,
)
from prodik.application.manage_profile import UpdateCurrentUserProfileInteractor
from prodik.application.services import AccessControlService


class ApplicationProvider(Provider):
    provides = provide_all(
        UpdateNodeInteractor,
        RegisterInteractor,
        LoginInteractor,
        AccessControlService,
        DeleteEdgeInteractor,
        RefreshTokenInteractor,
        UpdateEdgeWeightInteractor,
        IncrementEdgeWeightInteractor,
        UpdateCurrentUserProfileInteractor,
        UpdateCurrentUserPasswordInteractor,
        DecrementEdgeWeightInteractor,
        RegisterCompanyInteractor,
        DeleteContextInteractor,
        VerifyCompanyInteractor,
        CreateGroupInteractor,
        DeleteGroupInteractor,
        CreateNodeInteractor,
        DeleteNodeInteractor,
        DetachNodeInteractor,
        AttachNodeInteractor,
        CreateEdgeInteractor,
        CreateContextInteractor,
        scope=Scope.REQUEST,
    )
