import threading
from time import sleep


class threadlist:

    def __init__( self ):
        self.threadList = []
        t = threading.Thread( target=self.threadListCheck, name="ThreadManager" )
        t.start()

    def threadListCheck( self ):
        while True:
            # removing finished threads
            for t in self.threadList:
                if t['thread'].isAlive():
                    t['status'] = 'running'
                if not t['thread'].isAlive() and t['status'] == 'running':
                    print( "%s thread finished, removing" % ( t['name'] ) )
                    self.threadList.remove( t )
            # gather all running thread types - one type of thread can run only in one instance
            runningTypes = []
            for t in self.threadList:
                if not t['name'] in runningTypes and t['status'] == 'running':
                    runningTypes.append( t['name'] )
            # start any waiting thread
            for t in self.threadList:
                if not t['name'] in runningTypes:
                    t['status'] = 'running'
                    t['thread'].start()
                    print( "%s thread starting" % ( t['name'] ) )
                    runningTypes.append( t['name'] )
            sleep(1)


    def add( self, thr, name ):
        self.threadList.append( { 'name': name, 'thread': thr, 'status': 'waiting' } )


