import model.variables
from model.domain import Domain
from model.basecollection import BaseCollection


class DomainCollection(BaseCollection):
    _itemClass = Domain

    def sqlCondition( name, value ):
        if name == "name":
            return {  "sql": "domains.name=\%s", "vars": ( value ) }
        pass
