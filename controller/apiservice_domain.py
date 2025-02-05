import json
from controller.apiservice_base import ApiService_base
from model.routeresult import RouteResult
from model.domain import Domain
from model.domaincollection import DomainCollection
import model.variables as variables

class ApiService_domain( ApiService_base ):

    def getRoutes( self ):
        routes = [
            { "method": "get",    "auth": False, "target": self.getDomainList,        "pattern": r"^domain/list$" },
            { "method": "post",   "auth": False, "target": self.searchContent,        "pattern": r"^domain/(.+)/searchcontent$" },
            { "method": "get",    "auth": False, "target": self.getFolderContents,    "pattern": r"^domain/(.+)/content/(\d+)$" },
            { "method": "delete", "auth": False, "target": self.dropDomain,           "pattern": r"^domain/(.+)$" },
            { "method": "put",    "auth": True,  "target": self.putDomain,            "pattern": r"^domain/new$" },
        ]
        return routes


    def getFolderContents( self, groups, session ):
        top = int(session.getRequestHandler().get_argument( 't', 0 ))
        count = int(session.getRequestHandler().get_argument( 'c', 1000000000 ))
        dom = Domain.createByName( groups[1] )
        folder = dom.getFolder( folderId=groups[2] )
        if ( folder.isValid() or folder._id == 0 ):
            contents = []
            if ( int(top) <= 0 or top == None ):
                for f in folder.getSubFolders().getData():
                    contents.append( { 'type': 'folder', 'data': f } )
            for f in folder.getFiles( top, count ).getData( flags='wtapeinfo' ):
                contents.append( { 'type': 'file', 'data': f } )
            return RouteResult( 200, "ok", contents );
        else:
            return RouteResult( 404, "not-found", {} );


    def getDomainList( self, groups, session ):
        domains = DomainCollection()
        domains.setFilter( 'isActive', True )
        domainList = ()
        for dom in domains:
            domainList = domainList + ( { "id": dom.id(), "name": dom.name, "size": dom.getSize() }, )
        return RouteResult( 200, "ok", domainList )


    def dropDomain( self, groups, session ):
        try:
            aDomain = Domain.createByName( groups[1] )
            if ( aDomain.isValid ):
                aDomain.isActive = False
                aDomain.save()
                return RouteResult( 200, "ok", {} )
            else:
                return RouteResult( 404, "not found", {} )
        except Exception as e:
            return RouteResult( 500, "server-error", { "message": str(e) } )


    def putDomain( self, groups, session ):
        try:
            args = json.loads( self.request.body )
            if ( args['name'] != "" ):
                domain = Domain.createByName( args['name'] )
                if ( not domain.isValid() ):
                    domain.isActive = True
                    domain.save();
                    return RouteResult( 200, "ok", {} )
                elif ( domain.isActive == False ):
                    domain.isActive = True;
                    session.commit()
                    return RouteResult( 202, "domain-reactivated", {} )
                else:
                    return RouteResult( 201, "already-exists", {} )
        except Exception as e:
            return RouteResult( 500, "server-error", { "message": str(e) } )


    def searchContent( self, groups, session ):
        try:
            domain = Domain.createByName( groups[1] )
            if ( domain.isValid() == False ):
                return RouteResult( 404, "not-found", { 'message': 'domain-not-found' } )
            args = json.loads( self._apiServer.request.body )
            qstr = args["qstr"]
            page = args["page"]
#            qstr = session._requestHandler.get_argument( 'qstr', '' )
#            page = session._requestHandler.get_argument( 'page', 0 )
            try:
                page = int(page)
            except:
                page = 0
            return RouteResult( 200, "ok", { 'domain': domain.name, 'qstr': qstr, 'page': page, 'items': domain.search( qstr, page ) } )
        except Exception as e:
            return RouteResult( 500, "server-error", { "message": str(e) } )