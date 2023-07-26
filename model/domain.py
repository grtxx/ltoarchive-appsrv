import model.variables as variables
import sys
from model.folder import Folder
from model.file import File
from model.baseentity import BaseEntity


class Domain(BaseEntity):
    _tablename = variables.TablePrefix + 'domains'
    _fields = ( 'name' )
    
    def __init__( self, id = 0 ):
        super().__init__( id )
        

    @staticmethod
    def createByName( name ):
        db = variables.getScopedDb()
        cur = db.cursor()
        cur.execute( "SELECT id FROM domains WHERE name=%s", ( name, ) )
        id = cur.fetchOneDict()
        if ( id == None ):
            tp = Domain()
            tp.set( 'label', name )
            return tp
        else:
            return Domain( id["id"] )



    def addFolder( self, path ):
        return Folder.createByPathAndDomain( path, self )
    

    def getFolder( self, path ):
        return Folder.createByPathAndDomain( path, self )


    def addFileRecord( self, parentFolder, name, tape, hash ):
        from model.tape import Tape
        file = File.createFile( self, parentFolder, name, hash )
        if tape != None:
            file.addCopy( tape )
        return file
    

    def kill( self ):
        self.isActive = False
        self.save()

    
    def addFilesBulk( self, filelist ):
#        'path': os.path.join( dir, f ),
#        'hash': File.genHash( fspath ),
#        'domain': domain,
#        'tape': self,
#        'parentFolder': afolder
        db = variables.getScopedDb()
        recs = []
        recs2 = []
        delrecs = []
        for f in filelist:
            rec = ( f["tape"].id(), f["domain"].id(), None if f["parentFolder"] == None else f["parentFolder"].id(), f["hash"], f["startblock"] )
            rec2 = ( None if f["parentFolder"] == None else f["parentFolder"].id(), f["domain"].id(), f["name"], f["ext"], f["hash"], f["size"], f["created"] )
            delrec = ( None if f["parentFolder"] == None else f["parentFolder"].id(), f["domain"].id(), f["hash"] )
            recs.append( rec )
            recs2.append( rec2 )
            delrecs.append( delrec )
        if len( recs ) > 0:
            cur = db.cursor()
            cur.executemany( "INSERT IGNORE INTO %stapeitems (tapeId, domainId, folderId, hash, startblock) VALUES (%%s, %%s, %%s, %%s, %%s)" % ( variables.TablePrefix, ), recs )
            cur.reset()
            cur = db.cursor()
            cur.executemany( "DELETE FROM %sfiles WHERE parentFolderId=%%s AND domainId=%%s AND hash=%%s" % ( variables.TablePrefix, ), delrecs )
            cur.reset()
            cur = db.cursor()
            cur.executemany( "INSERT IGNORE INTO %sfiles (parentFolderId, domainId, name, ext, hash, size, created) VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s)" % ( variables.TablePrefix, ), recs2 )
            cur.reset()
        db.commit()


    def dropTape( self, tape ):
        db = variables.getScopedDb()
        db.cmd( "DELETE FROM `%stapeitems` WHERE domainId=%%s AND tapeId=%%s" % ( variables.TablePrefix, ), ( self.id(), tape.id(), ) )
