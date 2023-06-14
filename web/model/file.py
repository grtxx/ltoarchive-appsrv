import model.variables as variables
from model.folder import Folder
from model.baseentity import BaseEntity
import re
import os
import hashlib
import datetime

class File(BaseEntity):
    __tablename__ = variables.TablePrefix + 'File'
    _fields = ( 'domainId', 'folderId', 'name', 'ext', 'hash', 'size', 'created', 'isOnline', 'isDeleted' )
        
    @staticmethod
    def createFile( domain, parentFolder, name, hash, session=None):
        if ( session == None ):
            session = variables.getScopedSession()
        f = session.query(File).filter( File.parentFolder==parentFolder, File.name==name, File.archiveDomain==domain, File.hash == hash.encode('UTF-8') ).first();
        if f:
            return f
        else:
            file = File( archiveDomain=domain, parentFolder = parentFolder, hash = hash )
            session.add( file )
            file.setName( name )
            session.commit()
            return file


    def getFullPath( self ):
        if self.parentFolder:
            return self.parentFolder.getFullPath() + "/" + self.name
        else:
            return self.name
    

    def setName( self, name ):
        self.name = name
        g = re.match( r'(.+)\.([^\.]*)$', name )
        if g:
            self.ext = g.group(2)
        else:
            self.ext = ""
        return self
    

    def addCopy( self, tape, fullpath = None ):
        if ( fullpath == None ):
            fullpath = ""
            if ( self.parentFolder ):
                fullpath = self.parentFolder.getFullPath()
            fspath = os.path.join( variables.LTFSRoot, tape.label, self.archiveDomain.name, fullpath, self.name )
        else:
            fspath = fullpath
        if ( len( self.copies ) == 0 ):
                self.created = datetime.datetime.fromtimestamp( os.path.getmtime( fspath ) )
                self.size = os.path.getsize( fspath )
        ok = True
        for c in self.copies:
            if c.tape == tape:
                ok = False
        if ok:
            f2t = File2Tape.createByFileAndTape( self, tape )
            f2t.updateMeta( fspath )


def genHash( fspath ):
    name = os.path.basename( fspath )
    hsh = "%d-%d-%s" % ( os.path.getmtime( fspath ), os.path.getsize( fspath ), name )
    hash = hashlib.sha1( hsh.encode( 'UTF-8' ) ).hexdigest()
    return hash
