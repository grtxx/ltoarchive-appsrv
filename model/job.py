import model.variables as variables
import os
import datetime
import xattr
from model.baseentity import BaseEntity
from model.domain import Domain
from model.folder import Folder
import model.file

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

