import threading
import model.variables as variables

class BaseThread(threading.Thread):

    terminating = False
    _instanceId = -1
    manager = None

    def __init__( self, name ):
        threading.Thread.__init__( self )
        variables.Threads.add( self, name )

    def getInstanceId( self ):
        return self._instanceId
    
    def setInstanceId( self, id ):
        self._instanceId = id
