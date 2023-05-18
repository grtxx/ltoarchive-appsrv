import threading
import model.variables as variables
from model.tape import Tape

class TapeContentUpdaterThread( threading.Thread ):

    tapeName = ""

    def __init__( self, tapeName ):
        threading.Thread.__init__( self )
        self.name = "tapeContentUpdater"
        self.tapeName = tapeName
        variables.Threads.add( self, 'update-tape-content' )
    
    def run( self ):
        session = variables.getScopedSession()
        tape = Tape.createByName( self.tapeName, session=session )
        tape.updateContent()
        variables.dropScopedSession()

