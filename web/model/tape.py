import model.variables as variables
import os
import datetime
from model.baseentity import BaseEntity
from model.domain import Domain
from model.folder import Folder

class Tape(BaseEntity):
    _tablename = variables.TablePrefix + 'tapes'
    _fields = [ 'label', 'copyNumber', 'isAvailable', 'isActive', 'created' ]

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
        filelist = []
        while len(stack) > 0:
            dir = stack.pop()
            print( "[%s] %s - %s" % ( self.label, domain.name, dir ) )
            files = os.listdir( os.path.join( root, dir ) )
            afolder = domain.getFolder( dir )
            frecs = []
            for f in files:
                fspath = os.path.join( root, dir, f )
                if os.path.isfile( fspath ):
#                    files.append( (
#                        'path': os.path.join( root, dir, f ),
#                        'hash': File.genHash( path ),
#                        '
#                        'frec = domain.addFileRecord( afolder, f, None, hash )
#                    frec.addCopy( self, path )
                    pass
                else:
                    folder = Folder.createByNameParentAndDomain( f, afolder, domain )
                    if not folder.isValid():
                        folder.created = datetime.datetime.fromtimestamp( os.path.getmtime( fspath ) )
                        folder.save()
                    stack.append( os.path.join( dir, f ) )

