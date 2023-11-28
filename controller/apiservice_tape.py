from controller.apiservice_base import ApiService_base
from model.tapecollection import TapeCollection
from model.tape import Tape
from model.routeresult import RouteResult
import json
from controller.tapecontentupdaterthread import TapeContentUpdaterThread


class ApiService_tape( ApiService_base ):

    def getRoutes( self ):
        routes = [
            { "method": "get",    "auth": False, "target": self.getTapeList,          "pattern": r"^tape/list$" },
            { "method": "put",    "auth": True,  "target": self.tape_new,             "pattern": r"^tape/new$" },
            { "method": "delete", "auth": True,  "target": self.tape_drop,            "pattern": r"^tape/([^/]+)/drop$" },
            { "method": "patch",  "auth": True,  "target": self.tape_updateContent,   "pattern": r"^tape/([^/]+)/updatecontent$" },
        ]
        return routes


    def tape_new( self, groups, session ):
        #try:
            args = json.loads( self._apiServer.request.body )
            tape = Tape.createByName( args['label'] )
            tape.copyNumber = args['copyNumber']
            tape.isActive = 1
            tape.save()
            return RouteResult( 202, "tape-updated", {} )
        #except Exception as e:
        #    return RouteResult( 500, "server-error: %s" % str(e), str(e) )
        

    def tape_updateContent( self, groups, session ):
        tape = Tape.createByName( groups[1] )
        if tape.isValid():
            tc = TapeContentUpdaterThread( groups[1] )
            return RouteResult( 200, "queued", {} )
        else:
            return RouteResult( 404, "tape-not-found", {} )


    def tape_drop( self, groups, session ):
        tape = Tape.createByName( groups[1] )
        if tape.isValid():
            tape.drop()
            return RouteResult( 200, "ok", {} )
        else:
            return RouteResult( 404, "tape-not-found", {} )


    def getTapeList( self, groups, session ):
        tapes = TapeCollection()
        tapelist = []
        for tape in tapes:
            tapelist.append( { "id": tape.id(), "label": tape.get("label"), 'isAvailable': tape.get("isAvailable"), 'copyNumber': tape.get("copyNumber") } )
        return RouteResult( 200, "ok", tapelist )
