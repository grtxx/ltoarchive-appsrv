import threading
import importlib
from time import sleep


class threadlist:

    def __init__( self ):
        import model.variables as variables
        self.threadMax = variables.components
        self.threadList = []
        t = threading.Thread( target=self.threadListCheck, name="ThreadManager" )
        t.start()


    def getMaxInstanceCount( self, thdName ):
        return int(self.threadMax[ thdName ]['max']) if thdName in self.threadMax else 1



    def getThreadCount( self, thdName, mode='running' ):
        cnt = 0
        for t in self.threadList:
            if t['status'] == 'running' or t['thread'].isAlive():
                t['status'] = 'running'
            if ( t['name'] == thdName and ( t['status'] == 'running' or mode == 'all' ) ):
                cnt = cnt + 1
        return cnt

    def getNextInstanceId( self, thdName ):
        ok = False
        instanceId = -1
        while not ok:
            instanceId = instanceId + 1
            ok = True
            for t in self.threadList:
                if ( t['name'] == thdName ):
                    if t['thread'].getInstanceId() == instanceId:
                        ok = False
        return instanceId


    def canStartNew( self, threadName ):
        return self.getThreadCount( threadName, 'running' ) < self.getMaxInstanceCount( threadName )


    def canAddSpare( self, threadName ):
        return self.getThreadCount( threadName, 'all' ) < self.getMaxInstanceCount( threadName )


    def threadListCheck( self ):
        while True:
            # removing finished threads
            for t in self.threadList:

                if not t['thread'].isAlive() and t['status'] == 'running':
                    print( "%s thread finished, removing" % ( t['name'] ) )
                    self.threadList.remove( t )

            # start any waiting thread
            for t in self.threadList:
                if self.canStartNew( t['name'] ) and t['status'] != 'running':
                    print( "%s thread starting" % ( t['name'] ) )
                    t['thread'].setInstanceId( self.getNextInstanceId( t['name'] ) )
                    t['thread'].start()
                    t['status'] = 'running'

            for tm in self.threadMax:
                if self.canAddSpare( tm ) and self.threadMax[ tm ]['autocreate']:
                    print( "Creating new thread: %s" % ( tm ) )
                    module = importlib.import_module( self.threadMax[tm]['import'] )
                    cls = getattr( module, self.threadMax[tm]['className'] )
                    if cls != None:
                        cls()
            sleep(0.2)


    def add( self, thr, name ):
        thr.name = name
        thr.manager = self
        self.threadList.append( { 'name': name, 'thread': thr, 'status': 'waiting' } )


