from typing import Any
import model.variables
from model.baseentity import BaseEntity

class BaseCollection:
    _itemClass = BaseEntity
    _ids = ()
    _filters = ()
    _loaded = False
    _iterCursor = 0


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
        self._filters.append( { "name": name, "value": value } )


    def sqlCondition( name, value ):
        pass


    def buildFilterSql( self ):
        sqls = ( "1" )
        vars = ()
        for f in self._filters:
            cond = self.sqlCondition( f["name"], f["value"] )
            sqls.append( cond["sql"] )
            for k in cond["vars"]:
                vars.append( cond["vars"][k] )
        return { "sql": sqls, "vars": vars }
    

    def clear( self ):
        self._ids = ()
        self._loaded = True


    def load( self ):
        if ( self._loaded == False ):
            ditem = self._itemClass()

            db = model.variables.getScopedDb()
            cur = db.cursor()
            sqlcond = self.buildFilterSql()
            sql = "SELECT `%s` FROM `%s` WHERE %s ORDER BY %s" % ( ditem._idField, ditem._tablename, "(" + ( ") AND (".join( sqlcond["sql"] ) ) + ")", ditem._idField )            
            cur.execute( sql, sqlcond["vars"] )
            self._ids = ()
            item = cur.fetchOneDict()
            while item != None:
                self._ids = self._ids + ( item[ditem._idField], )
                item = cur.fetchOneDict()
            self._loaded = True

