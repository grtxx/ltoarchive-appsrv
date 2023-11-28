from model.job import Job
from model.basecollection import BaseCollection


class JobCollection(BaseCollection):
    _itemClass = Job

    def __init__( self ):
        super().__init__()
        self._filters = {}


    def sqlCondition( self, name, value ):
        #if name == "label":
        #    return {  "sql": "tapes.label=\%s", "vars": ( value ) }
        pass
