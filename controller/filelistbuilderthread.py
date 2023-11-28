import threading
import model.variables as variables

class filelistBuilderThread( threading.Thread ):

    def __init__( self, job ):
        threading.Thread.__init__( self )
        self.name = "filelistBuilder"
        self.job = job
        variables.Threads.add( self, 'job-filelist-builder' )
    
    def run( self ):
        self.job.buildFilelist()
        variables.dropScopedDb()
