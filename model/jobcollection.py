from model.job import Job
from model.basecollection import BaseCollection


class JobCollection(BaseCollection):
    _itemClass = Job

    def __init__( self ):
        super().__init__()
        self._filters = {}


    def sqlCondition( self, name, value ):
        if name == "status":
            if isinstance( value, str ):
                return {  "sql": "jobs.status=%s", "vars": [ value ] }
            else:
                return {  "sql": "jobs.status IN (" + "%s,"*len(value) + "-1)", "vars": value }
        if name == "max_nexttask":
            return {  "sql": "jobs.nexttask<%s", "vars": [ value ] }
        if name == "nexttask_sent":
            return {  "sql": "jobs.nexttask_sent=%s", "vars": [ value ] }
        pass
