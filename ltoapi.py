
import tornado.web
import re
import json
import time
import model.variables as variables
from model.routeresult import RouteResult
from model.session import Session
from controller.apiservice_project import ApiService_project
from controller.apiservice_user import ApiService_user
from controller.apiservice_domain import ApiService_domain
from controller.apiservice_tape import ApiService_tape
from controller.apiservice_job import ApiService_job


class LTOApi(tornado.web.RequestHandler):


    def initialize( self ):
        self._services = []
        self._sessions = {}
        self._lastSessionCleanup = 0
        self.addService( ApiService_domain() )
        self.addService( ApiService_project() )
        self.addService( ApiService_user() )
        self.addService( ApiService_tape() )
        self.addService( ApiService_job() )


    def addService( self, srvObj ):
        self._services.append( srvObj )
        srvObj.registerApiServer( self )

    def routes( self ):
        routes = [
            { "method": "get",    "auth": False, "target": self.getFolder,            "pattern": r"^content/([^/]+)/getfolder(/.*)" },
        ]
        for s in self._services:
            sroutes = s.getRoutes()
            for sr in sroutes:
                routes.append( sr )
        return routes
    

    def sessionCleanup( self ):
        if ( time.time() > self._lastSessionCleanup + 10 ):
            self._lastSessionCleanup = time.time()
            for s in self._sessions:
                if self._sessions[s].lastAction < time.time() + 600:
                    self._sessions.pop( s )


    def auth( self, r ):
        if ( r["auth"] == None or r["auth"] == False ):
            return None
        sessionId = self.request.headers.get( "X-SessionId")
        accessToken = self.request.headers.get( "X-AccessToken")
        queryGuid = self.request.headers.get( "X-QueryGuid")
        signature = self.request.headers.get( "X-Signature")
        self.sessionCleanup()
        session = None
        if sessionId != None:
            if ( self._sessions[ sessionId ] ):
                session = self._sessions[ sessionId ]
            else:
                session = Session.createByToken( sessionId )
        if accessToken != None:
            if ( accessToken in self._sessions ):
                session = self._sessions[ accessToken ]
                if not session.auth( queryGuid, signature ):
                    session = None
            else:
                session = Session.appAuth( accessToken, queryGuid, signature )
        if session == None:
            session = Session()
        return session


    def executeRoute( self, r, groups ):
        session = self.auth( r )
        if ( r["auth"]==False or session.userId != None ):
            db = variables.getScopedDb()
            db.commit()
            res = r["target"]( groups, session )
        else:
            res = RouteResult( 500, "query-not-authenticated", {} )
        self.output( res )


    def route( self, uri ):
        routeSucceeded = False
        for r in self.routes():
            if routeSucceeded == False:
                if ( r["method"] == self.request.method.lower() ):
                    reg = re.compile( r["pattern"] )
                    groups = reg.match( uri )
                    if ( groups ):
                        self.executeRoute( r, groups )
                        routeSucceeded = True
        if ( not routeSucceeded ):
            self.output( RouteResult( 404, "endpoint-not-found", {} ) )


    def output( self, result ):
        res = { "result": result.statustext, "data": result.data }
        self.write( json.dumps( res, indent=4, sort_keys=True, default=str ) )
        self._status_code = result.statuscode
        self.set_header( "Content-Type", "application/json" )


    def getFolder( self, groups, session ):
        arcdomain = groups.group(1)
        path = groups.group(2)
        print( "Archdomain: %s, Folder: %s" % ( arcdomain, path ) )
        return RouteResult( 200, "ok", arcdomain )


    def set_default_headers(self) -> None:
        super().set_default_headers()
        self.add_header( "X-ApiVersion", "0.1" )


    def put(self, uri ):
        self.route( uri )


    def get(self, uri ):
        self.route( uri )


    def delete( self, uri ):
        self.route( uri )


    def patch(self, uri ):
        self.route( uri )


    def post(self, uri ):
        self.route( uri )
