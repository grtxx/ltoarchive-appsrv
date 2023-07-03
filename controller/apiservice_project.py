from controller.apiservice_base import ApiService_base
from model.folder import Folder
from model.domain import Domain
from model.routeresult import RouteResult


class ApiService_project( ApiService_base ):

    def getRoutes( self ):
        routes = [
            { "method": "get",   "auth": True,  "target": self.projectInfo,           "pattern": r"^domain/([^/]+)/([^/]+)/getinfo$" }
        ]
        return routes


    def projectInfo( self, groups, session ):
        d = Domain.createByName( groups[1] )
        f = Folder.createByCodeAndDomain( groups[2], d )
        if f.isValid():
            f.updateSize()
            return RouteResult( 200, "ok", { 'folder': f.getData() } )
        else:
            return RouteResult( 404, "not-found", {} )

