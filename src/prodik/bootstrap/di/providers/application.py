from dishka import Provider, Scope, provide_all

from prodik.application.attach_node_to_group import (
    AttachNodeInteractor,
)
from prodik.application.authorization import (
    LoginInteractor,
    RefreshTokenInteractor,
    RegisterInteractor,
)
from prodik.application.create_context import CreateContextInteractor
from prodik.application.create_edge import CreateEdgeInteractor
from prodik.application.create_group import CreateGroupInteractor
from prodik.application.create_node import (
    CreateNodeInteractor,
)
from prodik.application.create_role import (
    CreateRoleInteractor,
)
from prodik.application.delete_context import (
    DeleteContextInteractor,
)
from prodik.application.delete_edge import DeleteEdgeInteractor
from prodik.application.delete_group import DeleteGroupInteractor
from prodik.application.delete_node import (
    DeleteNodeInteractor,
)
from prodik.application.delete_role import (
    DeleteRoleInteractor,
)
from prodik.application.detach_node_from_group import (
    DetachNodeInteractor,
)
from prodik.application.give_role_to_user import GiveRoleToUserInteractor
from prodik.application.manage_credentials import UpdateCurrentUserPasswordInteractor
from prodik.application.manage_profile import UpdateCurrentUserProfileInteractor
from prodik.application.receive_context_info import (
    GetContextByIdInteractor,
)
from prodik.application.receive_edge_info import GetEdgesByContextInteractor
from prodik.application.receive_group_info import GetGroupByIdInteractor
from prodik.application.receive_node_info import GetNodesByGroupInteractor
from prodik.application.receive_user_info import (
    GetCurrentUserInteractor,
    GetUserByUsernameInteractor,
)
from prodik.application.register_company import (
    RegisterCompanyInteractor,
)
from prodik.application.revoke_role_from_user import RevokeRoleFromUserInteractor
from prodik.application.services import AccessControlService
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
from prodik.application.update_role import (
    UpdateRoleInteractor,
)
from prodik.application.verify_company import VerifyCompanyInteractor


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
        GetGroupByIdInteractor,
        GetContextByIdInteractor,
        GetEdgesByContextInteractor,
        UpdateCurrentUserProfileInteractor,
        UpdateCurrentUserPasswordInteractor,
        SendOfferToCompanyInteractor,
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
        DeleteRoleInteractor,
        UpdateRoleInteractor,
        DeleteNodeInteractor,
        AcceptOfferInteractor,
        DeclineOfferInteractor,
        DetachNodeInteractor,
        CreateRoleInteractor,
        AttachNodeInteractor,
        CreateEdgeInteractor,
        GiveRoleToUserInteractor,
        RevokeRoleFromUserInteractor,
        scope=Scope.REQUEST,
    )
