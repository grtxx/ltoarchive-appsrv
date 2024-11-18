from controller.apiservice_base import ApiService_base
from model.routeresult import RouteResult
from model.jobcollection import JobCollection
import model.variables as Variables
import json


class ApiService_system( ApiService_base ):

    def getRoutes( self ):
        routes = [
            { "method": "get",    "auth": True,  "target": self.getDestinations,            "pattern": r"^destinations$" },
            { "method": "get",    "auth": True,  "target": self.getTasks,                   "pattern": r"^tasks$" },
            { "method": "get",    "auth": True,  "target": self.getWorkerCount,             "pattern": r"^system/workercount$" },
            { "method": "patch",  "auth": True,  "target": self.setWorkerCount,             "pattern": r"^system/workercount$" },
            { "method": "get",    "auth": True,  "target": self.getJobExecution,            "pattern": r"^system/jobexecution$" },
            { "method": "patch",  "auth": True,  "target": self.setJobExecution,            "pattern": r"^system/jobexecution$" },
        ]
        return routes


    def setWorkerCount( self, groups, session ):
        args = json.loads( self._apiServer.request.body )
        if 'worker-count' in args:
            try:
                wmax =  int(args['worker-count'])
                if wmax < 0:
                    wmax = 0
                if wmax > 500:
                    wmax = 500
                Variables.components['drive-controller']['max'] = wmax
                return RouteResult( 200, "ok", { 'worker-count': variables.components['drive-controller']['max'] } )
            except:
                return RouteResult( 501, "invalid-request-data", { 'error': 'invalid-request-data' } )
        else:
            return RouteResult( 501, "invalid-request-data", { 'error': 'invalid-request-data' } )


    def getWorkerCount( self, groups, session ):
        return RouteResult( 200, "ok", { 'worker-count': Variables.components['drive-controller']['max'] } )


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


    def getDestinations( self, groups, session ):
        dsts = []
        for d in Variables.destinations:
            dsts.append( { 'id': d, 'name': Variables.destinations[d]['name'] } )
        return RouteResult( 200, "ok", { 'destinations': dsts } )


    def getTasks( self, groups, session ):
        threads = []
        for d in Variables.Threads.threadList:
            threads.append( { 'name': d['name'], 'status': d['status'], 'message': d['message'], 'counters': d['counters'] } )
        return RouteResult( 200, "ok", { 'tasks': threads } )


