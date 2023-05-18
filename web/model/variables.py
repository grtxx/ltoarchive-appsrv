from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
from model.threadlist import threadlist
from sqlalchemy.orm import scoped_session
import threading 

DBEngine = sqlalchemy.create_engine( "mysql+mysqlconnector://lto:LTPs.sWRD@127.0.0.1:3306/um_archive?charset=utf8" )

def getSessionFactory():
    Session = scoped_session(sqlalchemy.orm.sessionmaker( bind=DBEngine ))
    return Session


def getScopedSession():
    tid = str(threading.current_thread().ident)
    if ( tid not in sessionMap ):
        scopedsession = getSessionFactory()
        sessionMap[tid] = scopedsession()
    return sessionMap[tid]

def dropScopedSession():
    tid = str(threading.current_thread().ident)
    if ( tid in sessionMap ):
        sessionMap[tid].close()
        del sessionMap[tid]


 
TablePrefix = ""
LTFSRoot = "/mnt/LTFS"
Threads = threadlist()
sessionMap = {}

Base = declarative_base()

# LTO related settings
vea_pre = "user."

