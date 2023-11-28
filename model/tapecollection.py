from model.tape import Tape
from model.basecollection import BaseCollection
import model.variables as variables

class TapeCollection(BaseCollection):
    _itemClass = Tape

    def __init__( self ):
        super().__init__()
        self._filters = {}


    def getFirstUsable( self ):
        usable = None
        lcn = 1024
        for t in self:
            if ( t.isAvailable == 1 and t.isActive == 1 and t.copyNumber < lcn ):
                lcn = t.copyNumber
                usable = t
        return usable


    def sqlCondition( self, name, value ):
        if name == "label":
            return {
                "sql": "tapes.label=\%s", 
                "vars": ( value ) 
            }
        elif name == "file":
            return {
                "sql": "tapes.id IN (SELECT tapeId FROM %stapeitems WHERE hash=%%s AND domainId=%%s AND folderId=%%s)" % (variables.TablePrefix),
                "vars": ( value.hash, value.domainId, value.parentFolderId ) 
            }
        pass
