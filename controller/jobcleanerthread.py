import threading
import time
import os.path
import model.variables as variables
from model.basethread import BaseThread
from model.jobcollection import JobCollection
from model.job import Job
import datetime

class JobCleanerThread( BaseThread ):

    def __init__( self ):
        BaseThread.__init__( self, 'job-cleaner' );
    

    def appendFolders( self, folders, path, basepath ):
        fp = os.path.dirname( path )
        while len( fp ) > len( basepath ):
            if fp not in folders:
                folders.append( fp )
            fp = os.path.dirname( fp )


    def dropFolders( self, folders ):
        folders.sort( key=lambda x: -1*len(x) )
        for f in folders:
            try:
                print( "Deleting folder: %s" %f )
                os.rmdir( f )
            except:
                pass

    def run( self ):
        db = variables.getScopedDb()
        while not self.terminating:
            jobs = JobCollection()
            jobs.setFilter( "status", [ "RESTORED", "DELETING" ] )
            jobs.setFilter( "max_nexttask", datetime.datetime.now() )
            for j in jobs:
                self.manager.setStatus( self, "Deleting job: %d" % j.id(), {} )
                j.status = 'DELETING'
                nfs = j.getNextFiles( 'RESTORED', 50 )
                folders = []
                while ( len(nfs) > 0 ):
                    for jf in nfs:
                        ok = False
                        if ( os.path.isfile( jf['dstpath'] ) ):
                            stt = os.stat( jf['dstpath'] )
                            if ( jf['filecreationdate'] == None or jf['filecreationdate'].timestamp() == stt.st_ctime ):
                                if ( stt.st_size == jf['size'] ):
                                    print( "Deleting: %s" % ( jf['dstpath'] ) )
                                    ok = True
                        else:
                            print( "Already deleted: %s" % ( jf['dstpath'] ) )
                            ok = True
                        if ( ok ):
                            self.appendFolders( folders, jf['dstpath'], jf['dstfs'] )        
                            try:
                                os.remove( jf['dstpath'] )
                            except:
                                pass
                            Job.updateJFStatus( jf, 'DELETED', False )
                            pass
                        else:
                            Job.updateJFStatus( jf, 'KEPT', False )
                            pass
                    Job.flushLog()
                    j.updateStatus()
                    nfs = j.getNextFiles( 'RESTORED', 50 )
                self.dropFolders( folders )
            Job.flushLog()
            self.manager.setStatus( self, "Idle", {} )
            time.sleep(30)
            db.commit()
