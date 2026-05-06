from dishka import Provider, Scope, provide_all

from prodik.application.authorization import (
    LoginInteractor,
    RefreshTokenInteractor,
    RegisterInteractor,
)
from prodik.application.services import AccessService, SessionService


class ApplicationProvider(Provider):
    provides = provide_all(
        AccessService,
        SessionService,
        RegisterInteractor,
        RefreshTokenInteractor,
        LoginInteractor,
        scope=Scope.REQUEST,
    )
