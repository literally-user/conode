from dishka import Provider, Scope, provide_all

from prodik.application.authorization import LoginInteractor, RegisterInteractor


class ApplicationProvider(Provider):
    provides = provide_all(RegisterInteractor, LoginInteractor, scope=Scope.REQUEST)
