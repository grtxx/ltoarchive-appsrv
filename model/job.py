import model.variables as variables
import datetime
from model.baseentity import BaseEntity
from model.file import File
import json

class Job(BaseEntity):
    _tablename = variables.TablePrefix + 'jobs'
    _fields = [ 'email', 'username', 'src', 'dststorage', 'created', 'status', 'nexttask' ]


    def __init__( self, id = 0 ):
        super().__init__( id )
        

    def getDefaultData(self):
        dt = super().getDefaultData()
        dt['created'] = datetime.datetime.now()
        return dt


    def drop( self ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            db.cmd( "DELETE FROM jobs WHERE id=%s", [ self.id() ] )


    def addFile( id, tapeId, dstpath ):
        pass

    def buildFilelist( self ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            print( "dropping old jobfiles" )
            db.cmd( "DELETE FROM jobfiles WHERE jobId=%s", [ self.id() ] )

            src = json.loads( self.src )
            print( src )

            for sel in src['sel']:
                type = sel['type']
                if ( type == 'file' ):
                    id = sel['data']['id']
                    f = File( id )
                    fps = f.getFirstUsableFileSysPathStruct()

                    print( f.getStartBlock( fps['tape'] ) )
                    print( fps )
            pass


