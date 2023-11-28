from controller.apiservice_base import ApiService_base
from model.job import Job
from model.jobcollection import JobCollection
from model.routeresult import RouteResult
import json


class ApiService_job( ApiService_base ):

    def getRoutes( self ):
        routes = [
            { "method": "get",    "auth": False, "target": self.getJobList,           "pattern": r"^job/list$" },
            { "method": "post",   "auth": True,  "target": self.postJob,              "pattern": r"^job/new$" },
            #{ "method": "put",    "auth": True,  "target": self.tape_new,             "pattern": r"^tape/new$" },
            #{ "method": "delete", "auth": True,  "target": self.tape_drop,            "pattern": r"^tape/([^/]+)/drop$" },
            #{ "method": "patch",  "auth": True,  "target": self.tape_updateContent,   "pattern": r"^tape/([^/]+)/updatecontent$" },
        ]
        return routes


    def getJobList( self, groups, session ):
        jobs = JobCollection()
        joblist = []
        for job in jobs:
            joblist.append( job.getData() )
        return RouteResult( 200, "ok", joblist )
        

    def postJob( self, groups, session ):
        params = json.loads( self._apiServer.request.body )
        if ( ('dststorage' in params) and ('username' in params) and ('src' in params) ):
            j = Job()
            j.src = json.dumps( params['src'] )
            j.dst = params['dststorage']
            j.email = params['email']
            j.username = params['username']
            j.status='PENDING'
            j.save()
            return RouteResult( 200, "ok", {} )
        else:
            return RouteResult( 405, "invalid-data", {} )

