import model.variables as variables
from model.baseentity import BaseEntity

class Folder(BaseEntity):
    _tablename = variables.TablePrefix + 'folders'
    _fields = [ 'domainId', 'name', 'size', 'created', 'isDeleted', 'parentFolderId' ]
    _orderField = "name"  


    def __init__( self, id = 0 ):
        super().__init__( id )
        self._fullpath = "."


    def __setattr__( self, name, value ):
        if ( name == "parentFolder" ):
            if value == None:
                self.parentFolderId = None
            elif not isinstance( value, Folder ):
                self.parentFolderId = int( value )
            else:
                self.parentFolderId = value.id()
        else:
            super().__setattr__( name, value )

    @staticmethod
    def createByNameParentAndDomain( name, parentFolder, domain ):
        db = variables.getScopedDb()
        f = None
        cur = db.cursor()
        if parentFolder == None:
            cur.execute( "SELECT id FROM %sfolders WHERE name=%%s AND ISNULL(parentFolderId) AND domainId=%%s" % (variables.TablePrefix, ), ( name, domain.id() ) )
        else:
            cur.execute( "SELECT id FROM %sfolders WHERE name=%%s AND parentFolderId=%%s AND domainId=%%s" % (variables.TablePrefix, ), ( name, parentFolder.id(), domain.id() ) )
        fId = cur.fetchOneDict()
        cur.reset()
        if ( fId == None ):
            f = Folder()
            f.parentFolder = parentFolder
            f.domainId = domain.id()
            f.name = name
        else:
            f = Folder( fId['id'] )
        return f


    @staticmethod
    def createByCodeAndDomain( code, domain ):
        db = variables.getScopedDb()
        f = None
        cur = db.cursor()
        cur.execute( "SELECT id FROM %sfolders WHERE name LIKE %%s AND ISNULL(parentFolderId) AND domainId=%%s" % (variables.TablePrefix, ), ( code + "%", domain.id() ) )
        fId = cur.fetchOneDict()
        cur.reset()
        if ( fId == None ):
            f = Folder()
            f.parentFolder = None
            f.domainId = domain.id()
            f.name = code
        else:
            f = Folder( fId['id'] )
        return f


    @staticmethod
    def createByPathAndDomain( path, domain ):
        db = variables.getScopedDb()
        path = path.split( "/" )
        currentParent = None
        f = None
        for p in path:
            if ( p != "" ):
                cur = db.cursor()
                if currentParent == None:
                    cur.execute( "SELECT id FROM %sfolders WHERE name=%%s AND ISNULL(parentFolderId) AND domainId=%%s LIMIT 1" % (variables.TablePrefix, ), ( p, domain.id() ) )
                else:
                    cur.execute( "SELECT id FROM %sfolders WHERE name=%%s AND parentFolderId=%%s AND domainId=%%s LIMIT 1" % (variables.TablePrefix, ), ( p, currentParent, domain.id() ) )
                fId = cur.fetchOneDict()
                cur.reset()
                if ( fId == None ):
                    f = Folder()
                    f.parentFolder = currentParent
                    f.domainId = domain.id()
                    f.name = p
                else:
                    f = Folder( fId['id'] )
                currentParent = f.id()
        return f
    

    def addTape( self, tape ):
        db = variables.getScopedDb()
        cur = db.cursor()
        cur.execute( "SELECT count(*) as cnt FROM %stapefolders WHERE folderId=%%s AND tapeId=%%s" % (variables.TablePrefix, ), ( self.id(), tape.id() ) )
        cnt = cur.fetchOneDict()
        cur.reset()
        if ( cnt['cnt'] == 0 ):
            cur = db.cursor()
            cur.execute( "INSERT INTO %stapefolders SET folderId=%%s, tapeId=%%s" % (variables.TablePrefix, ), ( self.id(), tape.id() ) )
            cur.reset()
        

    def getFullPath( self ):
        if ( self._fullPath == "." ):
            path = self.name
            pf = self
            while pf.isValid():
                pf = Folder( pf.parentFolderId )
                if pf.isValid():
                    path = pf.name + "/" + path
            self._fullPath = path
            return path
        else:
            return self._fullPath

    def getSubFolders( self ):
        from model.foldercollection import FolderCollection
        coll = FolderCollection()
        coll.setFilter( 'parentFolderId', self.id() )
        coll.setFilter( 'domainId', self.domainId )
        return coll


    def getDomain( self ):
        from model.domain import Domain
        return Domain( self.domainId )

    def getFiles( self ):
        from model.filecollection import FileCollection
        coll = FileCollection()
        coll.setFilter( 'parentFolderId', self.id() )
        coll.setFilter( 'domainId', self.domainId )
        return coll
    

    def updateSize( self ):
        if self.isValid():
            size = 0
            for f in self.getSubFolders():
                f.updateSize()
                size = size + f.size
            size = size + self.getFiles().getSumSize()
            self.size = size
            self.save()
