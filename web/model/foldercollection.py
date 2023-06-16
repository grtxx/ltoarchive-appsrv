from model.folder import Folder
from model.basecollection import BaseCollection


class FolderCollection(BaseCollection):
    _itemClass = Folder

    def sqlCondition( self, name, value ):
        if name == "name":
            return {  "sql": "folders.name=%s", "vars": [ value ] }
        elif name == "parentFolderId":
            return {  "sql": "folders.parentFolderId=%s", "vars": [ value ] }
        pass
