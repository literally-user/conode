from dishka import Provider, Scope, provide_all

from prodik.application.authorization import RegisterInteractor


class ApplicationProvider(Provider):
    provides = provide_all(RegisterInteractor, scope=Scope.REQUEST)
