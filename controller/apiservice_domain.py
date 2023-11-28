from controller.apiservice_base import ApiService_base
from model.routeresult import RouteResult
from model.domain import Domain
from model.domaincollection import DomainCollection
import model.variables as variables

class ApiService_domain( ApiService_base ):

    def getRoutes( self ):
        routes = [
            { "method": "get",    "auth": False, "target": self.getDomainList,        "pattern": r"^domain/list$" },
            { "method": "get",    "auth": True,  "target": self.getFolderContents,    "pattern": r"^domain/(.+)/content/(\d+)$" },
            { "method": "delete", "auth": False, "target": self.dropDomain,           "pattern": r"^domain/(.+)$" },
            { "method": "put",    "auth": True,  "target": self.putDomain,            "pattern": r"^domain/new$" },
        ]
        return routes


    def getFolderContents( self, groups, session ):
        dom = Domain.createByName( groups[1] )
        folder = dom.getFolder( folderId=groups[2] )
        if ( folder.isValid() or folder._id == 0 ):
            contents = []
            for f in folder.getSubFolders().getData():
                contents.append( { 'type': 'folder', 'data': f } )
            for f in folder.getFiles().getData( flags='wtapeinfo' ):
                contents.append( { 'type': 'file', 'data': f } )
            return RouteResult( 200, "ok", contents );
        else:
            return RouteResult( 404, "not-found", {} );


    def getDomainList( self, groups, session ):
        domains = DomainCollection()
        domainList = ()
        for dom in domains:
            domainList = domainList + ( { "id": dom.id(), "name": dom.name }, )
        return RouteResult( 200, "ok", domainList )


    def dropDomain( self, groups, session ):
        session = variables.getScopedSession()
        try:
            aDomain = session.query(ArchiveDomain).filter( ArchiveDomain.name==groups[1] ).first()
            if ( aDomain ):
                aDomain.isActive = False
                aDomain.kill()
                session.commit()
                return RouteResult( 200, "ok", {} )
            else:
                return RouteResult( 404, "not found", {} )
        except Exception as e:
            return RouteResult( 500, "server-error", { "message": str(e) } )


    def putDomain( self, groups, session ):
        session = variables.getScopedSession()
        try:
            args = json.loads( self.request.body )
            if ( args['name'] != "" ):
                domain = session.query(ArchiveDomain).filter( ArchiveDomain.name==args['name'] ).first()
                if ( not domain ):
                    session.add( ArchiveDomain(name=args['name'] ) )
                    session.commit()
                    return RouteResult( 200, "ok", {} )
                elif ( domain.isActive == False ):
                    domain.isActive = True;
                    session.commit()
                    return RouteResult( 202, "domain-reactivated", {} )
                else:
                    return RouteResult( 201, "already-exists", {} )
        except Exception as e:
            return RouteResult( 500, "server-error", { "message": str(e) } )
