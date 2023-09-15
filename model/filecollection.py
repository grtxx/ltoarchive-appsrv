from model.file import File
from model.basecollection import BaseCollection
import model.variables


class FileCollection(BaseCollection):
    _itemClass = File

    def sqlCondition( self, name, value ):
        if name == "name":
            return { "sql": "files.name=%s", "vars": [ value ] }
        elif name == "parentFolderId":
            if value != None and value != 0:
                return {  "sql": "files.parentFolderId=%s", "vars": [ value ] }
            else:
                return {  "sql": "ISNULL(files.parentFolderId)", "vars": [] }
        elif name == "domainId":
            return {  "sql": "files.domainId=%s", "vars": [ value ] }
        pass


    def getSumSize( self ):
        ditem = self._itemClass()
        db = model.variables.getScopedDb()
        cur = db.cursor()
        sqlcond = self.buildFilterSql()
        sql = "SELECT IFNULL(sum(size),0) AS sumsize FROM `%s` WHERE %s AND isOldVersion=0 AND isDeleted=0" % ( ditem._tablename, sqlcond["wherecondition"] )
        cur.execute( sql, sqlcond["vars"] )
        item = cur.fetchOneDict()
        cur.reset()
        return item["sumsize"]
