import model.variables as variables
from model.folder import Folder
from model.baseentity import BaseEntity
import uuid


class App(BaseEntity):
    _tablename = variables.TablePrefix + 'apps'
    _fields = ( 'name', 'appSecret' )
        

    @staticmethod
    def createByToken( token ):
        db = variables.getScopedDb()
        cur = db.cursor()
        cur.execute( "SELECT id FROM %sapps WHERE name=%%s" % ( variables.TablePrefix, ), ( token, ) )
        id = cur.fetchOneDict()
        if ( id == None ):
            return None
        else:
            return App( id["id"] )

    
    def getDefaultData( self ):
        dt = super().getDefaultData()
        dt["appSecret"] = uuid.v4()
        return dt

