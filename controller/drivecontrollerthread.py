import time
import subprocess
from model.tapecollection import TapeCollection
from model.basethread import BaseThread
from model.job import Job
import model.variables as variables
import shutil

class DriveControllerThread( BaseThread ):

    currentTape = None
    lastTape = None

    def __init__( self ):
        BaseThread.__init__( self, 'drive-controller' )
    

    def run( self ):
        idleTimer = 0
        print ( "%s started. InstanceId=%d" % ( self.name, self.getInstanceId() ) )
        while not self.terminating and self.getInstanceId() < self.manager.getMaxInstanceCount( self.name ):

            if self.currentTape == None: # no tape selected
                self.currentTape = TapeCollection.lockTape( self.getInstanceId() )
                if self.currentTape == None:
                    time.sleep(1)
                    idleTimer = idleTimer + 1
                else:
                    print( "                        "*self.getInstanceId(), "TAPE LOCK:" +self.currentTape.label )
            else:
                jf = Job.getNextFileForTape( self.currentTape )
                if jf != None:
                    try:
                        total, used, free = shutil.disk_usage( jf['dstfs'] )
                    except:
                        free = 10 * (2**30)
                    if ( free < 700 * (2**30) ):
                        job = Job( jf['jobId'] )
                        job.status = "FREESPACE-STOP"
                        job.save()
                        print( " "*25*self.getInstanceId(), "FREESPACE-STOP" )
                        time.sleep(30)
                    else:
                        print( " "*25*self.getInstanceId(), str(jf['tapeId'])+": "+str(jf['startblock']) )
                        Job.copyJF( jf )
                        idleTimer = 0

                else:
                    time.sleep(1)
                    idleTimer = idleTimer + 1
                    if idleTimer == 240 or TapeCollection.isThereJobForUnlockedTapes(): 
                        print( " "*25*self.getInstanceId(), "EJECT:" + self.currentTape.label )
                        subprocess.Popen( [ variables.leadm, "tape", "move", "-L", "homeslot", self.currentTape.label ] ).wait()
                        TapeCollection.releaseTape( self.getInstanceId() )
                        print( " "*25*self.getInstanceId(), "TAPE UNLOCK:" + self.currentTape.label )
                        self.currentTape = None
                    

        TapeCollection.releaseTape( self.getInstanceId() )