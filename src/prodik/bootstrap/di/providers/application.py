from dishka import Provider, Scope, provide_all

from prodik.application.authorization import (
    LoginInteractor,
    RefreshTokenInteractor,
    RegisterInteractor,
)
from prodik.application.manage_company import (
    RegisterCompanyInteractor,
    VerifyCompanyInteractor,
)
from prodik.application.manage_credentials import UpdateCurrentUserPasswordInteractor
from prodik.application.manage_profile import UpdateCurrentUserProfileInteractor


class ApplicationProvider(Provider):
    provides = provide_all(
        RegisterInteractor,
        LoginInteractor,
        RefreshTokenInteractor,
        UpdateCurrentUserProfileInteractor,
        UpdateCurrentUserPasswordInteractor,
        RegisterCompanyInteractor,
        VerifyCompanyInteractor,
        scope=Scope.REQUEST,
    )
