import model.variables as variables

from model.folder import Folder
from model.file import File
from model.baseentity import BaseEntity


class Domain(BaseEntity):
    _tablename = variables.TablePrefix + 'domains'
    _fields = ( 'name' )

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


    def dropTape( self, tape ):
        db = variables.getScopedDb()
        #db.cmd( "DELETE FROM `%stapecontents` WHERE tapeId=%%s" % ( variables.TablePrefix, ), ( tape.id(), ) )
        #db.cmd( "DELETE FROM `%sfiles` WHERE tapeId=%%s" % ( variables.TablePrefix, ), ( tape.id(), ) )
        #db.cmd( "DELETE FROM `%sfolders` WHERE tapeId=%%s" % ( variables.TablePrefix, ), ( tape.id(), ) )
