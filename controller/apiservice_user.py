from controller.apiservice_base import ApiService_base
from model.folder import Folder
from model.domain import Domain
from model.routeresult import RouteResult


class ApiService_user( ApiService_base ):

    def getRoutes( self ):
        routes = [
            { "method": "get",    "auth": True, "target": self.getMe,           "pattern": r"^me$" }
        ]
        return routes


    def getMe( self, groups, session ):
        if session.user != None:
            return RouteResult( 200, "ok", { 'me': session.user.getData() } )
        else:
            return RouteResult( 404, "not-found", {} )

