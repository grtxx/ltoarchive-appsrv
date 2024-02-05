from controller.apiservice_base import ApiService_base
from model.job import Job
from model.jobcollection import JobCollection
from model.routeresult import RouteResult
from controller.filelistbuilderthread import FilelistBuilderThread
import json


class ApiService_job( ApiService_base ):

    def getRoutes( self ):
        routes = [
            { "method": "get",    "auth": False, "target": self.getJobList,           "pattern": r"^job/list$" },
            { "method": "post",   "auth": True,  "target": self.postJob,              "pattern": r"^job/new$" },
            { "method": "get",    "auth": False, "target": self.getJob,               "pattern": r"^job/(\d+)$" },
            { "method": "delete", "auth": True,  "target": self.dropJob,              "pattern": r"^job/(\d+)$" },

            #{ "method": "put",    "auth": True,  "target": self.tape_new,             "pattern": r"^tape/new$" },
            #{ "method": "delete", "auth": True,  "target": self.tape_drop,            "pattern": r"^tape/([^/]+)/drop$" },
            #{ "method": "patch",  "auth": True,  "target": self.tape_updateContent,   "pattern": r"^tape/([^/]+)/updatecontent$" },
        ]
        return routes

    def getJob( self, groups, session ):
        job = Job( groups[1] )
        if job.isValid():
            return RouteResult( 200, "ok", { 'job': job.getData() } )
        else:
            return RouteResult( 404, "not-found", {} )


    def dropJob( self, groups, session ):
        job = Job( groups[1] )
        if job.isValid():
            job.drop()
            return RouteResult( 200, "ok", {} )
        else:
            return RouteResult( 404, "not-found", {} )


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
            j.dststorage = params['dststorage']
            j.email = params['email']
            j.username = params['username']
            j.webhook = params['webhook']
            j.status='PENDING'
            j.save()
            tc = FilelistBuilderThread( j )
            return RouteResult( 200, "ok", {} )
        else:
            return RouteResult( 405, "invalid-data", {} )

