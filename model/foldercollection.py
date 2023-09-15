from model.folder import Folder
from model.basecollection import BaseCollection


class FolderCollection(BaseCollection):
    _itemClass = Folder

    def sqlCondition( self, name, value ):
        if name == "name":
            return {  "sql": "folders.name=%s", "vars": [ value ] }
        elif name == "parentFolderId":
            if value != None and value != 0:
                return {  "sql": "folders.parentFolderId=%s", "vars": [ value ] }
            else:
                return {  "sql": "ISNULL(folders.parentFolderId)", "vars": [] }
        elif name == "domainId":
            return {  "sql": "folders.domainId=%s", "vars": [ value ] }
        pass
