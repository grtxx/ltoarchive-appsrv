from controller.apiservice_base import ApiService_base
from model.routeresult import RouteResult
import model.variables as Variables


class ApiService_system( ApiService_base ):

    def getRoutes( self ):
        routes = [
            { "method": "get",    "auth": False, "target": self.getDestionations,           "pattern": r"^destinations$" },
            { "method": "get",    "auth": False, "target": self.getTasks,                   "pattern": r"^tasks$" },
        ]
        return routes


    def getDestionations( self, groups, session ):
        dsts = []
        for d in Variables.destinations:
            dsts.append( { 'id': d, 'name': Variables.destinations[d]['name'] } )
        return RouteResult( 200, "ok", { 'destinations': dsts } )


    def getTasks( self, groups, session ):
        threads = []
        for d in Variables.Threads.threadList:
            threads.append( { 'name': d['name'], 'status': d['status'] } )
        return RouteResult( 200, "ok", { 'tasks': threads } )


