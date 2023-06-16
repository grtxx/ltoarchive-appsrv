import mysql.connector
import mysql.connector.cursor_cext
from model.threadlist import threadlist
import threading 


# no result execute on db
def cmd( self, query, params=None ):
    cur = self.cursor()
    cur.execute( query, params )
    cur.reset()
    self.commit()


# Extending cursor class with a new fetchOneDict method
def fetchonedict( self ):
    row = self.fetchone()
    if row != None:
        d = {}
        for idx,col in enumerate( self.description ):
            d[ col[0] ] = row[idx]
        return d
    else:
        return None
    
mysql.connector.cursor_cext.CMySQLCursor.fetchOneDict = fetchonedict
mysql.connector.CMySQLConnection.cmd = cmd


def getDbConnection():
    db = mysql.connector.connect(
        host="localhost",
        user="lto",
        password="LTPs.sWRD",
        database="um_archive"
    )
    cur = db.cursor()
    cur.execute( "SET NAMES utf8", () )
    db.commit()

    return db


def getScopedDb():
    tid = str(threading.current_thread().ident)
    if ( tid not in sessionMap ):
        scopedDb = getDbConnection()
        sessionMap[tid] = scopedDb
    sessionMap[tid].ping( reconnect=True )
    return sessionMap[tid]

def dropScopedDb():
    tid = str(threading.current_thread().ident)
    if ( tid in sessionMap ):
        sessionMap[tid].close()
        del sessionMap[tid]


 
TablePrefix = ""
LTFSRoot = "/mnt/LTFS"
Threads = threadlist()
sessionMap = {}

# LTO related settings
vea_pre = "user."

