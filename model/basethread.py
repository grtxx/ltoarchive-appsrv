import threading
import model.variables as variables

class BaseThread(threading.Thread):

    def __init__( self, name ):
        self._instanceId = -1
        self.terminating = False
        self.manager = None
        threading.Thread.__init__( self )
        variables.Threads.add( self, name )

    def getInstanceId( self ):
        return self._instanceId
    
    def setInstanceId( self, id ):
        self._instanceId = id
