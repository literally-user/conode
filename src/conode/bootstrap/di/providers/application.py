from dishka import Provider, Scope, provide_all

from conode.application.attach_node_to_group import (
    AttachNodeInteractor,
)
from conode.application.detach_node_from_group import (
    DetachNodeInteractor,
)
from conode.application.manage_context import (
    CreateContextInteractor,
    DeleteContextInteractor,
)
from conode.application.manage_edge import CreateEdgeInteractor, DeleteEdgeInteractor
from conode.application.manage_group import CreateGroupInteractor, DeleteGroupInteractor
from conode.application.manage_node import CreateNodeInteractor, DeleteNodeInteractor
from conode.application.manage_profile import UpdateCurrentUserProfileInteractor
from conode.application.manage_role import (
    CreateRoleInteractor,
    DeleteRoleInteractor,
    UpdateRoleInteractor,
)
from conode.application.manage_user_rights import (
    GiveRoleToUserInteractor,
    RevokeRoleFromUserInteractor,
)
from conode.application.receive_context_info import (
    GetContextByIdInteractor,
)
from conode.application.receive_graph_statistics import (
    FindShortestPathInteractor,
    GetNodeNeighboursInteractor,
)
from conode.application.receive_group_info import GetGroupByIdInteractor
from conode.application.receive_node_info import GetNodesByGroupInteractor
from conode.application.receive_user_info import (
    GetCurrentUserInteractor,
    GetUserByUsernameInteractor,
)
from conode.application.register_company import (
    RegisterCompanyInteractor,
)
from conode.application.services import (
    AccessControlService,
    OfferAcceptanceService,
    OfferSendingService,
    RoleManagmentService,
)
from conode.application.share_graph import (
    AcceptOfferInteractor,
    DeclineOfferInteractor,
    SendOfferToCompanyInteractor,
)
from conode.application.update_edge_weight import (
    DecrementEdgeWeightInteractor,
    IncrementEdgeWeightInteractor,
    UpdateEdgeWeightInteractor,
)
from conode.application.update_node import (
    UpdateNodeInteractor,
)
from conode.application.verify_company import VerifyCompanyInteractor


class ApplicationProvider(Provider):
    provides = provide_all(
        UpdateNodeInteractor,
        AccessControlService,
        OfferAcceptanceService,
        OfferSendingService,
        DeleteEdgeInteractor,
        UpdateEdgeWeightInteractor,
        IncrementEdgeWeightInteractor,
        GetGroupByIdInteractor,
        GetContextByIdInteractor,
        UpdateCurrentUserProfileInteractor,
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
