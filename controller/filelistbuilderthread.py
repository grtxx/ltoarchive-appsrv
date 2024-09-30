import model.variables as variables
from model.basethread import BaseThread

class FilelistBuilderThread( BaseThread ):

    def __init__( self, job ):
        BaseThread.__init__( self, 'filelistbuilder' )
        self.job = job
    
    def run( self ):
        self.manager.setMessage( self, "Building filelist" )
        self.job.buildFilelist()
        variables.dropScopedDb()
        self.manager.setMessage( self, "Shutting down" )
