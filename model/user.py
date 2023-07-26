import model.variables as variables
from model.folder import Folder
from model.baseentity import BaseEntity


class User(BaseEntity):
    _tablename = variables.TablePrefix + 'users'
    _fields = [ 'username', 'fullname', 'pwhash', 'origin' ]
        
    
    def getDefaultData( self ):
        dt = super().getDefaultData()
        dt["origin"] = 'LOCAL'
        return dt

