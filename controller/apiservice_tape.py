from controller.apiservice_base import ApiService_base
from model.tapecollection import TapeCollection
from model.tape import Tape
from model.routeresult import RouteResult
import model.variables as variables
import json
from controller.tapecontentupdaterthread import TapeContentUpdaterThread
from controller.tapecontentclonerthread import TapeContentClonerThread


class ApiService_tape( ApiService_base ):

    def getRoutes( self ):
        routes = [
            { "method": "get",    "auth": False, "target": self.getTapeList,          "pattern": r"^tape/list$" },
            { "method": "put",    "auth": True,  "target": self.tape_new,             "pattern": r"^tape/new$" },
            { "method": "get",    "auth": True,  "target": self.getWorkerCount,       "pattern": r"^tape/workercount$" },
            { "method": "patch",  "auth": True,  "target": self.setWorkerCount,       "pattern": r"^tape/workercount$" },
            { "method": "delete", "auth": True,  "target": self.tape_drop,            "pattern": r"^tape/([^/]+)/drop$" },
            { "method": "patch",  "auth": True,  "target": self.tape_updateContent,   "pattern": r"^tape/([^/]+)/updatecontent$" },
            { "method": "patch",  "auth": True,  "target": self.tape_clone,           "pattern": r"^tape/([^/]+)/cloneto/([^/]+)" },
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
                variables.components['drive-controller']['max'] = wmax
                return RouteResult( 200, "ok", { 'worker-count': variables.components['drive-controller']['max'] } )
            except:
                return RouteResult( 501, "invalid-request-data", {} )
        else:
            return RouteResult( 501, "invalid-request-data", {} )


    def getWorkerCount( self, groups, session ):
        return RouteResult( 200, "ok", { 'worker-count': variables.components['drive-controller']['max'] } )


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


    def tape_clone( self, groups, session ):
        tape = Tape.createByName( groups[1] )
        tape2 = Tape.createByName( groups[2] )
        if tape.isValid() and tape2.isValid():
            tc = TapeContentClonerThread( groups[1], groups[2] )
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

