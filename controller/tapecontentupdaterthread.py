import threading
import model.variables as variables
from model.tape import Tape
from model.basethread import BaseThread

class TapeContentUpdaterThread( BaseThread ):

    def __init__( self, tapeName ):
        BaseThread.__init__( self, 'tapecontentupdater' )
        self.tapeName = tapeName

    
    def run( self ):
        self.manager.setMessage( self, "Updating content for %s" % ( self.tapeName ) )
        tape = Tape.createByName( self.tapeName )
        tape.updateContent()
        variables.dropScopedDb()
        self.manager.setMessage( self, "Shutting down" )
