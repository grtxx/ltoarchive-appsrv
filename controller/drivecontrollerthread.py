import time
import subprocess
from model.tapecollection import TapeCollection
from model.basethread import BaseThread
from model.job import Job
import model.variables as variables
import shutil
import sys

class DriveControllerThread( BaseThread ):

    currentTape = None
    lastTape = None

    def __init__( self ):
        BaseThread.__init__( self, 'drive-controller' )
    

    def run( self ):
        counters = { 'CURRENT_TAPE': '', 'COPIED_BYTES': 0, 'JOBID': 0 }
        idleTimer = 0
        copiedsize = 0
        print ( "%s started. InstanceId=%d" % ( self.name, self.getInstanceId() ) )
        sys.stdout.flush()
        while not self.terminating and self.getInstanceId() < self.manager.getMaxInstanceCount( self.name ):

            if self.currentTape == None: # no tape selected
                self.manager.setStatus( self, "Idle", counters )
                self.currentTape = TapeCollection.lockTape( self.getInstanceId() )
                if self.currentTape == None:
                    time.sleep(1)
                    idleTimer = idleTimer + 1
                else:
                    copiedsize = 0
                    counters['CURRENT_TAPE'] = self.currentTape.label
                    self.manager.setMessage( self, "Locking tape %s" % ( self.currentTape.label ) )
                    self.manager.setCounters( self, counters )
                    sys.stdout.flush()
                    #subprocess.Popen( [ variables.leadm, "tape", "move", "-L", "drive", self.currentTape.label ] ).wait()
            else:
                jf = Job.getNextFileForTape( self.currentTape )
                if jf != None:
                    job = Job( jf['jobId'] )
                    counters['JOBID'] = jf['jobId']
                    try:
                        total, used, free = shutil.disk_usage( jf['dstfs'] )
                    except:
                        free = 10 * (2**30)
                    if ( free < 500 * (2**30) and copiedsize > 100*1024*1024*1024 ):
                        copiedsize = 0
                        job.status = "FREESPACE-STOP"
                        job.save()
                        counters['CURRENT_TAPE'] = ''
                        self.manager.setStatus( self, "Idle, FREESPACE-STOP", counters )
                        time.sleep(10)
                    else:
                        if ( job.status != "RESTORING" ):
                            job.status = "RESTORING"
                            job.save()
                        self.manager.setStatus( self, "Restoring: %s" % ( jf['srcpath'] ), counters )
                        Job.copyJF( jf )
                        copiedsize = copiedsize + jf['size']
                        counters['COPIED_BYTES'] = copiedsize
                        self.manager.setCounters( self, counters )
                        idleTimer = 0
                else:
                    counters['JOBID'] = 0
                    counters['COPIED_BYTES'] = 0
                    self.manager.setStatus( self, "Idle", counters )
                    time.sleep(1)
                    idleTimer = idleTimer + 1
                    if idleTimer == 600 or TapeCollection.isThereJobForUnlockedTapes(): 
                        self.manager.setStatus( self, "Releasing tape: %s" % ( self.currentTape.label ), counters )
                        subprocess.Popen( [ variables.leadm, "tape", "move", "-L", "homeslot", self.currentTape.label ] ).wait()
                        TapeCollection.releaseTape( self.getInstanceId() )
                        counters['CURRENT_TAPE'] = ''
                        self.manager.setStatus( self, "Idle", counters )
                        self.currentTape = None
        TapeCollection.releaseTape( self.getInstanceId() )