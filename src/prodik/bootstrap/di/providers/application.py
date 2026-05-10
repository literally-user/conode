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
from prodik.application.receive_group_info import GetGroupsByCurrentCompanyInteractor
from prodik.application.receive_nodes_info import GetNodesByGroupInteractor
from prodik.application.receive_user_info import (
    GetCurrentUserInteractor,
    GetUserByUsernameInteractor,
)
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
        GetGroupsByCurrentCompanyInteractor,
        UpdateCurrentUserProfileInteractor,
        UpdateCurrentUserPasswordInteractor,
        DecrementEdgeWeightInteractor,
        GetUserByUsernameInteractor,
        GetNodesByGroupInteractor,
        RegisterCompanyInteractor,
        GetCurrentUserInteractor,
        CreateContextInteractor,
        VerifyCompanyInteractor,
        DeleteContextInteractor,
        CreateGroupInteractor,
        DeleteGroupInteractor,
        CreateNodeInteractor,
        DeleteNodeInteractor,
        DetachNodeInteractor,
        AttachNodeInteractor,
        CreateEdgeInteractor,
        scope=Scope.REQUEST,
    )
