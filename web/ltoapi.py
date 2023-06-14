
import tornado.web
import re
import json
import model.variables as variables
from model.tape import Tape
from model.domain import Domain
from model.tapecollection import TapeCollection
from model.domaincollection import DomainCollection
from controller.tapecontentupdaterthread import TapeContentUpdaterThread


class routeResult:
    def __init__( self, statuscode, statustext, data ):
        self.statuscode = statuscode
        self.statustext = statustext
        self.data = data


class LTOApi(tornado.web.RequestHandler):

    def initialize( self ):
        pass

    def routes( self ):
        return [
            { "method": "get",    "target": self.getFolder,            "pattern": r"^content/([^/]+)/getfolder(/.*)" },
            { "method": "get",    "target": self.getTapeList,          "pattern": r"^tape/list$" },
            { "method": "get",    "target": self.getDomainList,        "pattern": r"^domain/list$" },

            { "method": "delete", "target": self.dropDomain,           "pattern": r"^domain/(.+)$" },

            { "method": "put",    "target": self.putDomain,            "pattern": r"^domain/new$" },
            { "method": "put",    "target": self.tape_new,             "pattern": r"^tape/new$" },
            { "method": "patch",  "target": self.tape_updateContent,   "pattern": r"^tape/([^/]+)/updatecontent$" },
        ]
    

    def route( self, uri ):
        routeSucceeded = False
        for r in self.routes():
            if ( r["method"] == self.request.method.lower() ):
                reg = re.compile( r["pattern"] )
                groups = reg.match( uri )
                if ( groups ):
                    res = r["target"]( groups )
                    self.output( res )
                    routeSucceeded = True
        if ( not routeSucceeded ):
            self.output( routeResult( 404, "endpoint-not-found", {} ) )


    def output( self, result ):
        res = { "result": result.statustext, "data": result.data }
        self.write( json.dumps( res ) )
        self._status_code = result.statuscode
        self.set_header( "Content-Type", "application/json" )




    def tape_new( self, groups ):
        #try:
            args = json.loads( self.request.body )
            tape = Tape.createByName( args['label'] )
            tape.set( 'copyNumber', args['copyNumber'] )
            tape.set( 'isActive', 1 )
            tape.save()
            return routeResult( 202, "tape-updated", {} )
        #except Exception as e:
        #    return routeResult( 500, "server-error: %s" % str(e), str(e) )
        

    def tape_updateContent( self, groups ):
        tape = Tape.createByName( groups[1] )
        if tape.isValid():
            tc = TapeContentUpdaterThread( groups[1] )
            return routeResult( 200, "queued", {} )
        else:
            return routeResult( 404, "tape-not-found", {} )


    def dropDomain( self, groups ):
        session = variables.getScopedSession()
        try:
            aDomain = session.query(ArchiveDomain).filter( ArchiveDomain.name==groups[1] ).first()
            if ( aDomain ):
                aDomain.isActive = False
                aDomain.kill()
                session.commit()
                return routeResult( 200, "ok", {} )
            else:
                return routeResult( 404, "not found", {} )
        except Exception as e:
            return routeResult( 500, "server-error", { "message": str(e) } )


    def putDomain( self, groups ):
        session = variables.getScopedSession()
        try:
            args = json.loads( self.request.body )
            if ( args['name'] != "" ):
                domain = session.query(ArchiveDomain).filter( ArchiveDomain.name==args['name'] ).first()
                if ( not domain ):
                    session.add( ArchiveDomain(name=args['name'] ) )
                    session.commit()
                    return routeResult( 200, "ok", {} )
                elif ( domain.isActive == False ):
                    domain.isActive = True;
                    session.commit()
                    return routeResult( 202, "domain-reactivated", {} )
                else:
                    return routeResult( 201, "already-exists", {} )
        except Exception as e:
            return routeResult( 500, "server-error", { "message": str(e) } )


    def getTapeList( self, groups ):
        tapes = TapeCollection()
        tapelist = []
        for tape in tapes:
            tapelist.append( { "label": tape.get("label"), 'isAvailable': tape.get("isAvailable"), 'copyNumber': tape.get("copyNumber") } )
        return routeResult( 200, "ok", tapelist )


    def getDomainList( self, groups ):
        domains = DomainCollection()
        domainList = ()
        for dom in domains:
            domainList = domainList + ( { "id": dom.id(), "name": dom.name }, )
        return routeResult( 200, "ok", domainList )


    def getFolder( self, groups ):
        arcdomain = groups.group(1)
        path = groups.group(2)
        print( "Archdomain: %s, Folder: %s" % ( arcdomain, path ) )
        return routeResult( 200, "ok", arcdomain )



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
