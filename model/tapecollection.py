from model.tape import Tape
from model.basecollection import BaseCollection


class TapeCollection(BaseCollection):
    _itemClass = Tape

    def __init__( self ):
        super().__init__()
        self._filters = {}


    def sqlCondition( self, name, value ):
        if name == "label":
            return {  "sql": "tapes.label=\%s", "vars": ( value ) }
        pass
