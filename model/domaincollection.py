import model.variables
from model.domain import Domain
from model.basecollection import BaseCollection


class DomainCollection(BaseCollection):
    _itemClass = Domain

    def sqlCondition( self, name, value ):
        if name  == "isActive":
            if ( value == True or value == 1 ):
                value = "1"
            else:
                value = "0"
            return {  "sql": "domains.isActive=%s", "vars": ( value ) }
        if name == "name":
            return {  "sql": "domains.name=%s", "vars": ( value ) }
        pass
