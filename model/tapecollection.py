from model.tape import Tape
from model.basecollection import BaseCollection
import model.variables as variables

class TapeCollection(BaseCollection):
    _itemClass = Tape

    def __init__( self ):
        super().__init__()
        self._filters = {}


    @staticmethod
    def isThereJobForUnlockedTapes():
        db = variables.getScopedDb()
        db.commit()
        cur = db.cursor()
        cur.execute( "SELECT count(*) AS c FROM `%stapes` WHERE ISNULL(lockedBy) AND id IN (SELECT DISTINCT tapeId FROM jobfiles WHERE status='WAITING')" % ( variables.TablePrefix ) )
        return (cur.fetchOneDict())['c'] > 0


    @staticmethod
    def lockTape( instanceId ):
        db = variables.getScopedDb()
        db.commit()
        TapeCollection.releaseTape( instanceId )
        db.commit()
        db.start_transaction()
        db.cmd( "UPDATE tapes SET lockedBy=%s WHERE id=(SELECT t.id FROM tapes AS t "
            + "INNER JOIN jobfiles AS jf ON (t.id=jf.tapeId) "
            + "INNER JOIN jobs AS j ON (j.id=jf.jobId) "
            + "WHERE ISNULL(t.lockedBy) AND jf.status='WAITING' AND j.status IN ('WAITING', 'RESTORING') "
            + "ORDER BY jf.created "
            + "LIMIT 1)", ( instanceId, ) )
        t = Tape.createByInstanceId( instanceId )
        if not t.isValid():
            t = None
        db.commit()
        return t


    @staticmethod
    def releaseTape( instanceId ):
        db = variables.getScopedDb()
        db.cmd( "UPDATE tapes SET lockedby=NULL WHERE lockedBy=%s", ( instanceId, ) )
        db.commit()


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
