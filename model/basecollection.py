from typing import Any
import model.variables
from model.baseentity import BaseEntity

class BaseCollection:
    _itemClass = BaseEntity


    def __init__( self ):
        super().__init__()
        self._ids = []
        self._filters = {}
        self._loaded = False
        self._iterCursor = 0


    def __iter__( self ):
        self.load()
        self._iterCursor = 0
        return self
    
    def __next__( self ):
        if ( len( self._ids ) < self._iterCursor+1 ):
            raise StopIteration
        res = self._itemClass( self._ids[ self._iterCursor ] )
        self._iterCursor = self._iterCursor + 1
        return res

    def setFilter( self, name, value ):
        self._filters[name] = value


    def sqlCondition( self, name, value ):
        pass


    def buildFilterSql( self ):
        sqls = [ "1" ]
        vars = []
        for k in self._filters:
            cond = self.sqlCondition( k, self._filters[k] )
            #cond["sql"] = cond["sql"].replace( "%", "%%" )
            if ( cond != None ):
                sqls.append( cond["sql"] )
                for k in cond["vars"]:
                    vars.append( k )
        return { "sql": sqls, "vars": vars, "wherecondition": "(" + ") AND (".join( sqls ) + ")" }
    

    def clear( self ):
        self._ids = []
        self._loaded = True


    def load( self ):
        if ( self._loaded == False ):
            ditem = self._itemClass()

            db = model.variables.getScopedDb()
            cur = db.cursor()
            sqlcond = self.buildFilterSql()
            sql = "SELECT `%s` FROM `%s` WHERE %s ORDER BY %s" % ( ditem._idField, ditem._tablename, sqlcond["wherecondition"], ditem._orderField + ", " + ditem._idField )            
            cur.execute( sql, sqlcond["vars"] )
            self._ids = []
            item = cur.fetchOneDict()
            while item != None:
                self._ids.append( item[ditem._idField] )
                item = cur.fetchOneDict()
            self._loaded = True


    def getData( self ):
        dt = []
        for item in self:
            dt.append( item.getData() )
        return dt