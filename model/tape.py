import model.variables as variables
import os
import datetime
import xattr
from model.baseentity import BaseEntity
from model.domain import Domain
from model.folder import Folder
import model.file

class Tape(BaseEntity):
    _tablename = variables.TablePrefix + 'tapes'
    _fields = [ 'label', 'copyNumber', 'isAvailable', 'isActive', 'created' ]


    def __init__( self, id = 0 ):
        super().__init__( id )
        

    @staticmethod
    def createByName( name ):
        db = variables.getScopedDb()
        cur = db.cursor()
        cur.execute( "SELECT id FROM `%stapes` WHERE label=%%s" % ( variables.TablePrefix ), ( name, ) )
        id = cur.fetchOneDict()
        if ( id == None ):
            tp = Tape()
            tp.set( 'label', name )
            return tp
        else:
            return Tape( id["id"] )


    def getDefaultData(self):
        dt = super().getDefaultData()
        dt['created'] = datetime.datetime.now()
        return dt


    def getRoot( self ):
        return os.path.join( variables.LTFSRoot, self.label )


    def drop( self ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            print( "Dropping tape..." )
            db.cmd( "DELETE FROM tapeitems WHERE tapeId=%s", [ self.id() ] )
            db.cmd( "DELETE FROM tapes WHERE id=%s", [ self.id() ] )


    def updateContent( self ):
        cartRoot = os.listdir( self.getRoot() )
        domains = []
        for d in cartRoot:
            if ( os.path.isdir( os.path.join( self.getRoot(), d ) ) ):
                domains.append( d )
        for d in domains:
            self.updateDomainContent( d )


    def updateDomainContent( self, d ):
        domain = Domain.createByName( d )
        domain.dropTape( self )
        root = os.path.join( self.getRoot(), d )
        stack = [ "" ]
        topfolders = []
        folders = []
        while len(stack) > 0:
            filelist = []
            dir = stack.pop()
            print( "[%s] %s - %s" % ( self.label, domain.name, dir ) )
            files = os.listdir( os.path.join( root, dir ) )
            afolder = domain.getFolder( dir )
            for f in files:
                fspath = os.path.join( root, dir, f )
                if os.path.isfile( fspath ):
                    stb = 0
                    try:
                        rawattr = xattr.getxattr( fspath, "%sltfs.startblock" % ( variables.vea_pre, ) )
                        if ( rawattr != None ):
                            stb = int( str( bytearray( rawattr ), 'UTF-8' ) )
                    except:
                        pass
                    n, ext = os.path.splitext( f )
                    filelist.append( {
                        'name': f,
                        'ext': ext,
                        'path': os.path.join( dir, f ),
                        'hash': model.file.genHash( fspath ),
                        'domain': domain,
                        'tape': self,
                        'parentFolder': afolder,
                        'startblock': stb,
                        'size': os.path.getsize( fspath ),
                        'created': datetime.datetime.fromtimestamp( os.path.getmtime( fspath ) )
                    } )
                    pass
                else:
                    folder = Folder.createByNameParentAndDomain( f, afolder, domain )
                    if not folder.isValid():
                        folder.created = datetime.datetime.fromtimestamp( os.path.getmtime( fspath ) )
                        folder.save()
                    stack.append( os.path.join( dir, f ) )
                    if afolder == None:
                        topfolders.append( folder )
                    folders.append( folder )
            domain.addFilesBulk( filelist )
        self._updateOldVersions( folders )
        self._updateTopFolders( topfolders )


    def _updateTopFolders( self, topfolders ):
        print( "Updating folder size..." )
        for topfolder in topfolders:
            print( "\t%s" % ( topfolder.name, ) )
            topfolder.updateSize()


    def _updateOldVersions( self, folders ):
        db = variables.getScopedDb()
        print( "Updating shadow files..." )
        db.cmd( "CREATE TEMPORARY TABLE updateOldV (id int primary key not null)" )
        for folder in folders:
            print( "\t%s" % ( folder.name, ) )
            db.cmd( "UPDATE %sfiles SET isOldVersion=0 WHERE parentFolderId=%%s" % (variables.TablePrefix, ), [ folder.id() ] )
            db.cmd( "INSERT IGNORE INTO updateOldV SELECT id FROM %sfiles AS f WHERE parentFolderId=%%s AND domainId=%%s AND EXISTS (SELECT id FROM %sfiles AS ff WHERE ff.created>f.created AND ff.parentFolderId=f.parentFolderId AND ff.domainId=f.domainId AND ff.name=f.name)" % ( variables.TablePrefix, variables.TablePrefix,  ), [ folder.id(), folder.domainId ] )
        print( "\tcommit..." )            
        db.cmd( "UPDATE %sfiles SET isOldVersion=1 WHERE id IN (SELECT id FROM updateOldV)" % ( variables.TablePrefix, ) )
        db.cmd( "DROP TABLE updateOldV" )
        db.commit()