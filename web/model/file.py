import model.variables as variables
from model.folder import Folder
from model.baseentity import BaseEntity
import re
import os
import hashlib
import datetime

class File(BaseEntity):
    _tablename = variables.TablePrefix + 'files'
    _fields = ( 'domainId', 'folderId', 'name', 'ext', 'hash', 'size', 'created', 'isOnline', 'isDeleted' )
        

    def __setattr__( self, name, value ):
        if ( name == "parentFolder" ):
            if value == None:
                self.parentFolderId = None
            else:
                self.parentFolderId = value.id()
        else:
            super().__setattr__( name, value )

    @staticmethod
    def createFile( domain, parentFolder, name, hash):
        db = variables.getScopedDb()
        f = None
        cur = db.cursor()
        if parentFolder == None:
            cur.execute( "SELECT id FROM %sfiles WHERE name=%%s AND ISNULL(parentFolderId) AND domainId=%%s" % (variables.TablePrefix, ), ( name, domain.id() ) )
        else:
            cur.execute( "SELECT id FROM %sfiles WHERE name=%%s AND parentFolderId=%%s AND domainId=%%s" % (variables.TablePrefix, ), ( name, parentFolder.id(), domain.id() ) )
        fId = cur.fetchOneDict()
        cur.reset()
        if ( fId == None ):
            f = File()
            f.parentFolder = parentFolder
            f.domainId = domain.id()
            f.name = name
            f.hash = hash
        else:
            f = File( fId['id'] )
        return f


    def getFullPath( self ):
        if self.parentFolder:
            return self.parentFolder.getFullPath() + "/" + self.name
        else:
            return self.name
    

def genHash( fspath ):
    name = os.path.basename( fspath )
    hsh = "%d-%d-%s" % ( os.path.getmtime( fspath ), os.path.getsize( fspath ), name )
    hash = hashlib.sha1( hsh.encode( 'UTF-8' ) ).hexdigest()
    return hash
