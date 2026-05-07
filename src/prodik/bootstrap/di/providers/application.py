from dishka import Provider, Scope, provide_all

from prodik.application.authorization import (
    LoginInteractor,
    RefreshTokenInteractor,
    RegisterInteractor,
)


class ApplicationProvider(Provider):
    provides = provide_all(
        RegisterInteractor, LoginInteractor, RefreshTokenInteractor, scope=Scope.REQUEST
    )
