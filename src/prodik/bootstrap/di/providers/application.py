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
from prodik.application.manage_contexts import CreateContextInteractor
from prodik.application.manage_credentials import UpdateCurrentUserPasswordInteractor
from prodik.application.manage_edges import CreateEdgeInteractor
from prodik.application.manage_group import CreateGroupInteractor, DeleteGroupInteractor
from prodik.application.manage_node import CreateNodeInteractor, DeleteNodeInteractor
from prodik.application.manage_profile import UpdateCurrentUserProfileInteractor
from prodik.application.services import AccessControlService


class ApplicationProvider(Provider):
    provides = provide_all(
        RegisterInteractor,
        LoginInteractor,
        AccessControlService,
        RefreshTokenInteractor,
        UpdateCurrentUserProfileInteractor,
        UpdateCurrentUserPasswordInteractor,
        RegisterCompanyInteractor,
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
