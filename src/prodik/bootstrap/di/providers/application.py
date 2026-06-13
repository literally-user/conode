from dishka import Provider, Scope, provide_all

from prodik.application.attach_node_to_group import (
    AttachNodeInteractor,
)
from prodik.application.authorization import (
    LoginInteractor,
    RefreshTokenInteractor,
    RegisterInteractor,
)
from prodik.application.detach_node_from_group import (
    DetachNodeInteractor,
)
from prodik.application.manage_context import (
    CreateContextInteractor,
    DeleteContextInteractor,
)
from prodik.application.manage_credentials import UpdateCurrentUserPasswordInteractor
from prodik.application.manage_edge import CreateEdgeInteractor, DeleteEdgeInteractor
from prodik.application.manage_group import CreateGroupInteractor, DeleteGroupInteractor
from prodik.application.manage_node import CreateNodeInteractor, DeleteNodeInteractor
from prodik.application.manage_profile import UpdateCurrentUserProfileInteractor
from prodik.application.manage_role import (
    CreateRoleInteractor,
    DeleteRoleInteractor,
    UpdateRoleInteractor,
)
from prodik.application.manage_user_rights import (
    GiveRoleToUserInteractor,
    RevokeRoleFromUserInteractor,
)
from prodik.application.receive_context_info import (
    GetContextByIdInteractor,
)
from prodik.application.receive_edge_info import GetEdgesByContextInteractor
from prodik.application.receive_graph_statistics import (
    FindShortestPathInteractor,
    GetNodeNeighboursInteractor,
)
from prodik.application.receive_group_info import GetGroupByIdInteractor
from prodik.application.receive_node_info import GetNodesByGroupInteractor
from prodik.application.receive_user_info import (
    GetCurrentUserInteractor,
    GetUserByUsernameInteractor,
)
from prodik.application.register_company import (
    RegisterCompanyInteractor,
)
from prodik.application.services import (
    AccessControlService,
    OfferAcceptanceService,
    OfferSendingService,
    RoleManagmentService,
)
from prodik.application.share_graph import (
    AcceptOfferInteractor,
    DeclineOfferInteractor,
    SendOfferToCompanyInteractor,
)
from prodik.application.update_edge_weight import (
    DecrementEdgeWeightInteractor,
    IncrementEdgeWeightInteractor,
    UpdateEdgeWeightInteractor,
)
from prodik.application.update_node import (
    UpdateNodeInteractor,
)
from prodik.application.verify_company import VerifyCompanyInteractor


class ApplicationProvider(Provider):
    provides = provide_all(
        UpdateNodeInteractor,
        RegisterInteractor,
        LoginInteractor,
        AccessControlService,
        OfferAcceptanceService,
        OfferSendingService,
        DeleteEdgeInteractor,
        RefreshTokenInteractor,
        UpdateEdgeWeightInteractor,
        IncrementEdgeWeightInteractor,
        GetGroupByIdInteractor,
        GetContextByIdInteractor,
        GetEdgesByContextInteractor,
        UpdateCurrentUserProfileInteractor,
        UpdateCurrentUserPasswordInteractor,
        SendOfferToCompanyInteractor,
        DecrementEdgeWeightInteractor,
        GetUserByUsernameInteractor,
        FindShortestPathInteractor,
        GetNodesByGroupInteractor,
        RegisterCompanyInteractor,
        GetCurrentUserInteractor,
        CreateContextInteractor,
        VerifyCompanyInteractor,
        DeleteContextInteractor,
        CreateGroupInteractor,
        DeleteGroupInteractor,
        CreateNodeInteractor,
        DeleteRoleInteractor,
        RoleManagmentService,
        UpdateRoleInteractor,
        DeleteNodeInteractor,
        AcceptOfferInteractor,
        DeclineOfferInteractor,
        DetachNodeInteractor,
        GetNodeNeighboursInteractor,
        CreateRoleInteractor,
        AttachNodeInteractor,
        CreateEdgeInteractor,
        GiveRoleToUserInteractor,
        RevokeRoleFromUserInteractor,
        scope=Scope.REQUEST,
    )
