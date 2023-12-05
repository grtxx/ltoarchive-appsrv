import threading
import time
import os.path
import model.variables as variables
from model.tapecollection import TapeCollection
from model.basethread import BaseThread

class TapeCheckerThread( BaseThread ):

    def __init__( self ):
        BaseThread.__init__( self, 'tape-checker' );
    

    def run( self ):
        while not self.terminating:
            TC = TapeCollection()
            for tape in TC:
                if os.path.isdir( "%s/%s" % ( variables.LTFSRoot, tape.label ) ):
                    tape.isAvailable = 1
                else:
                    tape.isAvailable = 0
                tape.save()
                #print( tape.label )
            TC = None
            time.sleep(30)