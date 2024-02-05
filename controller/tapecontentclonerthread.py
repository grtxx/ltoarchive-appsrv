import threading
import model.variables as variables
from model.tape import Tape
from model.basethread import BaseThread

class TapeContentClonerThread( BaseThread ):

    def __init__( self, tapeName, dstTapeName ):
        BaseThread.__init__( self, 'tapecontentcloner' )
        self.tapeName = tapeName
        self.dstTapeName = dstTapeName

    
    def run( self ):
        tape = Tape.createByName( self.tapeName )
        dstTape = Tape.createByName( self.dstTapeName )
        tape.cloneTo( dstTape )
        variables.dropScopedDb()
