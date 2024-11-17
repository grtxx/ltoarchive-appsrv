from controller.apiservice_base import ApiService_base
from model.routeresult import RouteResult
from model.jobcollection import JobCollection
import model.variables as Variables


class ApiService_system( ApiService_base ):

    def getRoutes( self ):
        routes = [
            { "method": "get",    "auth": False, "target": self.getDestionations,           "pattern": r"^destinations$" },
            { "method": "get",    "auth": False, "target": self.getTasks,                   "pattern": r"^tasks$" },
            { "method": "get",    "auth": True,  "target": self.getJobExecution,            "pattern": r"^jobexecution$" },
            { "method": "patch",  "auth": True,  "target": self.setJobExecution,            "pattern": r"^jobexecution$" },
        ]
        return routes


    def getJobExecution( self, groups, session ):
        return RouteResult( 200, "ok", { 'jobexecution': Variables.jobExecution } )


    def setJobExecution( self, groups, session ):
        args = json.loads( self._apiServer.request.body )
        if ( 'jobexecution' in args ):
            Variables.jobExecution = args['jobexecution']
            if ( Variables.jobExecution ):
                jobs = JobCollection()
                jobs.setFilter( 'status', 'PENDING' )
                for j in jobs:
                    j.execute();
        return RouteResult( 200, "ok", { 'jobexecution': Variables.jobExecution } )


    def getDestionations( self, groups, session ):
        dsts = []
        for d in Variables.destinations:
            dsts.append( { 'id': d, 'name': Variables.destinations[d]['name'] } )
        return RouteResult( 200, "ok", { 'destinations': dsts } )


    def getTasks( self, groups, session ):
        threads = []
        for d in Variables.Threads.threadList:
            threads.append( { 'name': d['name'], 'status': d['status'], 'message': d['message'], 'counters': d['counters'] } )
        return RouteResult( 200, "ok", { 'tasks': threads } )


