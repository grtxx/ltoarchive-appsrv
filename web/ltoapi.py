
import tornado.web
import re
import json
from model.tape import Tape
from model.archivedomain import ArchiveDomain

class LTOApi(tornado.web.RequestHandler):

    def initialize( self, session ):
        self.session = session


    def set_default_headers(self) -> None:
        super().set_default_headers()
        self.add_header( "X-ApiVersion", "0.1" )


    def output( self, httpcode, errortext, output ):
        res = { "result": errortext, "data": output }
        self.write( json.dumps( res ) )
        self._status_code = httpcode
        self.set_header( "Content-Type", "application/json" )


    def put(self, uri ):
        if ( uri == "tape/new" ):
            try:
                args = json.loads( self.request.body )
            finally:
                self.output( 500, "server-error", {} )
        if ( uri == "archivedomain/new" ):
            try:
                args = json.loads( self.request.body )
                if ( args['name'] != "" ):
                    isDomainExists = self.session.query(ArchiveDomain).filter( ArchiveDomain.name==args['name'] ).count()
                    if ( isDomainExists == 0 ):
                        self.session.add( ArchiveDomain(name=args['name'] ) )
                        self.session.commit()
                    else:
                        self.output( 201, "already-exists", {} )
                        return None
            except:
                self.output( 500, "server-error", {} )
                return None
            self.output( 200, "OK", {} )
            return None



    def get(self, uri ):
        if ( uri == "tape/list" ):
            tapelist = []
            tapes = self.session.query(Tape).all()
            for tape in tapes:
                tapelist.add( { "label": tape.label, 'isAvailable': tape.isAvailable } )
            self.output( 200, "ok", tapelist )            

        if ( uri == "archivedomain/list" ):
            arcdomains = []
            domains = self.session.query(ArchiveDomain).filter(ArchiveDomain.isActive==True)

            for domain in domains:
                arcdomains.append( { "name": domain.name, "isExclusiveOnTapes": domain.isExclusiveOnTapes } )
            self.output( 200, "ok", arcdomains )            

        if ( re.match( r"getfolder\/(.*)", uri ) ):
            grps = re.match( r"(^content\/([^\/]*)\/getfolder\/(.*)", uri )
            if ( grps ):
                arcdomain = grps.group(1)
                path = grps.group(2)
                print( "Archdomain: %s, Folder: %s" % ( arcdomain, path ) )
                self.output( 200, "ok", arcdomains )            
