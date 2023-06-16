import model.variables
from model.tape import Tape
from model.basecollection import BaseCollection


class TapeCollection(BaseCollection):
    _itemClass = Tape

    def sqlCondition( name, value ):
        if name == "label":
            return {  "sql": "tapes.label=\%s", "vars": ( value ) }
        pass
