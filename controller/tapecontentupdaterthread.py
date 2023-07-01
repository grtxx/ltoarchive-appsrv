import threading
import model.variables as variables
from model.tape import Tape

class TapeContentUpdaterThread( threading.Thread ):

    def __init__( self, tapeName ):
        threading.Thread.__init__( self )
        self.name = "tapeContentUpdater"
        self.tapeName = tapeName
        variables.Threads.add( self, 'update-tape-content' )
    
    def run( self ):
        tape = Tape.createByName( self.tapeName )
        tape.updateContent()
        variables.dropScopedDb()
