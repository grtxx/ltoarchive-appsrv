import threading
import time
import os.path
import model.variables as variables
from model.basethread import BaseThread
from model.jobcollection import JobCollection
import datetime

class JobCheckerThread( BaseThread ):

    def __init__( self ):
        BaseThread.__init__( self, 'job-checker' );
    

    def run( self ):
        db = variables.getScopedDb()
        while not self.terminating:
            self.manager.setStatus( self, "Checking jobs", {} )
            jobs = JobCollection()
            jobs.setFilter( "status", "RESTORED" )
            jobs.setFilter( "max_nexttask", datetime.datetime.now()+datetime.timedelta(days=2) )
            jobs.setFilter( "nexttask_sent", 0 )
            for j in jobs:
                print( "Sending delete warning for job: %s" % j.id() )
                r = j.sendDeleteWarning()
                if ( r != None ):
                    j.nexttask_sent = 1
                else:
                    print( j )
                    j.nexttask_sent = 2
                j.save()
            self.manager.setStatus( self, "Idle", {} ) 
            time.sleep(10)
            db.commit()
