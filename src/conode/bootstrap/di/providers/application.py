from dishka import Provider, Scope, provide_all

from conode.application.authorization import (
    LoginInteractor,
    RefreshTokenInteractor,
    RegisterInteractor,
)
from conode.application.services import AccessService, SessionService


class ApplicationProvider(Provider):
    provides = provide_all(
        AccessService,
        SessionService,
        RegisterInteractor,
        RefreshTokenInteractor,
        LoginInteractor,
        scope=Scope.REQUEST,
    )
