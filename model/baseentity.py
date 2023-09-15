from typing import Any
import model.variables as variables
import copy


class BaseEntity():
    _tablename = variables.TablePrefix + 'tapes'
    _idField = "id"
    _orderField = "id"

    def __init__( self, id=0 ):
        #self._fields = ()
        self._cached = False
        self._data = {}
        self._dataInDb = {}
        self._id = id


    def __getattr__(self, name: str) -> Any:
        self.cacheIf()
        if ( self._data != None ):
            if name in self._data:
                return self._data[ name ]
        return None


    def isValid( self ) -> bool:
        self.cacheIf()
        return ( self.id() != None )

    def __setattr__(self, name: str, value: Any) -> None:
        if name not in self._fields:
            super().__setattr__( name, value )
        else:
            self.cacheIf()
            self._data[ name ] = value
  

    def cache( self ):
        db = variables.getScopedDb()
        cur = db.cursor()
        cur.execute( "SELECT * FROM %s WHERE %s=%%s" % ( self._tablename, self._idField ), ( self._id, ) )
        return cur.fetchOneDict()


    def getDefaultData( self ):
        return {}


    def id( self ) -> int:
        if self._id > 0:
            return int( self._id )
        return None


    def set( self, name, value ):
        self.cacheIf()
        if self._data == None:
            self._data = {}
        self._data[name] = value


    def get( self, name, defval=None ):
        self.cacheIf()
        if name in self._data:
            return self._data[name]
        else:
            return defval


    def cacheIf( self ):
        if not self._cached:
            self._data = self.cache()
            self._dataInDb = copy.copy( self._data )
            if self._data == None:
                self._data = self.getDefaultData()
                self._id = 0
            self._cached = True
            if self._idField in self._data:
                self._id = self._data[ self._idField ]
            else:
                self._id = 0


    def changedFields( self ):
        self.cacheIf()
        cf = ()
        for i in self._fields:
            ok = False
            if ( self._dataInDb == None ):
                ok = True
            else:
                if i not in self._dataInDb:
                    ok = True
                else:
                    if self._data[i] != self._dataInDb[i]:
                        ok = True
            if ok:
                cf = cf + ( i, )
        return cf


    def save( self ):
        fields = self.changedFields()
        sqlfields = ()
        sqlvals = ()
        for c in fields:
            sqlfields = sqlfields + ( "`"+c+"`=%s", )
            if c in self._data:
                sqlvals = sqlvals + ( self._data[c], )
            else:
                sqlvals = sqlvals + ( None, )

        if len( sqlvals ) > 0:
            db = variables.getScopedDb()
            if self.id() == None:
                cur = db.cursor()
                cur.execute( "INSERT INTO %s () VALUES ()" % ( self._tablename, ) )
                self._id = cur.lastrowid;
                cur.reset()
            sql = "UPDATE %s SET %s WHERE %s=%d" % ( self._tablename, ", ".join( sqlfields ), self._idField, self._id )
            db.cmd( sql, sqlvals )
            db.commit()


    def getData( self ):
        self.cacheIf()
        return self._data