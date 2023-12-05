import model.variables as variables
from model.folder import Folder
from model.baseentity import BaseEntity
import re
import os
import hashlib
import datetime

class File(BaseEntity):
    _tablename = variables.TablePrefix + 'files'
    _fields = [ 'domainId', 'folderId', 'name', 'ext', 'hash', 'size', 'created', 'isOnline', 'isDeleted' ]

    def __setattr__( self, name, value ):
        if ( name == "parentFolder" ):
            if value == None:
                self.parentFolderId = None
            else:
                self.parentFolderId = value.id()
        else:
            super().__setattr__( name, value )


    def __getattr__( self, name ):
        if ( name == "parentFolder" ):
            return self.localCacheGet( 'parentfolder', lambda x: Folder( self.parentFolderId ) )
        else:
            return super().__getattr__( name )


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


    def getFirstUsableTape( self ):
        return self.localCacheGet( 'firstusabletape', lambda x: self.getTapes().getFirstUsable() )


    def getFirstUsableFileSysPathStruct( self ):
        from model.domain import Domain
        vfspath = self.getFullPath()
        d = Domain( self.domainId )
        t = self.getFirstUsableTape()
        if ( t ):
            return { 
                'tape': t, 
                'srcpath': "%s/%s/%s/%s" % ( variables.LTFSRoot, t.label, d.name, vfspath ),
                'vfspath': vfspath 
            }
        else:
            return None
        pass


    def getFullPath( self ):
        if self.parentFolder:
            return self.parentFolder.getFullPath() + "/" + self.name
        else:
            return self.name
        

    def getTapeInfo( self ):
        db = variables.getScopedDb()
        cur = db.cursor( dictionary=True)
        cur.execute( ("SELECT tapeId, tapes.label, startblock FROM %stapeitems " +
                     "INNER JOIN %stapes ON (tapes.id=tapeId) WHERE hash=%%s AND domainId=%%s AND folderId=%%s ORDER BY copyNumber") % (variables.TablePrefix, variables.TablePrefix, ), (self.hash, self.domainId, self.parentFolderId ) )
        ti = cur.fetchall()
        return ti
    

    def getStartBlock( self, tape ):
        db = variables.getScopedDb()
        cur = db.cursor( dictionary=True)
        cur.execute( ("SELECT IFNULL(startblock,-1) AS stb FROM %stapeitems WHERE hash=%%s AND domainId=%%s AND folderId=%%s AND tapeId=%%s LIMIT 1") % (variables.TablePrefix, ), (self.hash, self.domainId, self.parentFolderId, tape.id() ) )
        ti = cur.fetchall()
        return ti[0]['stb']
    

    def getTapes( self ):
        from model.tapecollection import TapeCollection
        def getTapesFromDb( self ):
            tapes = TapeCollection()
            tapes.setFilter( 'file', self )
            return tapes
        
        return self.localCacheGet( 'tapes', getTapesFromDb )
    

    def getData( self, flags="" ):
        dt = super().getData( flags )
        flags = flags.split(",")
        try:
            if ( flags.index( "wtapeinfo" ) >=0 ):
                dt['tapes'] = self.getTapeInfo()
        except:
            pass
        return dt
    

def genHash( fspath ):
    name = os.path.basename( fspath )
    hsh = "%d-%d-%s" % ( os.path.getmtime( fspath ), os.path.getsize( fspath ), name )
    hash = hashlib.sha1( hsh.encode( 'UTF-8' ) ).hexdigest()
    return hash
