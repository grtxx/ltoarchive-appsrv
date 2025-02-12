from typing import Any
import model.variables as variables
import datetime
from model.baseentity import BaseEntity
from model.file import File
from model.folder import Folder
from model.domain import Domain
from controller.filelistbuilderthread import FilelistBuilderThread
import json
import os
import shutil
import requests
import sys


_updatelog = []


class Job(BaseEntity):
    _tablename = variables.TablePrefix + 'jobs'
    _fields = [ 'email', 'username', 'src', 'dststorage', 'created', 'finished', 'status', 'nexttask', 'nexttask_sent', 'webhook', 'lasterror' ]
    _orderField = "created DESC, id DESC"


    def __init__( self, id = 0 ):
        super().__init__( id )
        

    def __setattr__(self, name: str, value: Any) -> None:
        if name == 'status':
            if self.status != value:
                if value=='RESTORED':
                    self.finished=datetime.datetime.now()
                    self.nexttask = datetime.datetime.now() + datetime.timedelta( days=7 )
                    self.nexttask_sent = 0
        super().__setattr__(name, value)
        if name == 'status' and value == 'RESTORED':
            if ( self.webhook != None and self.webhook != "" ):
                r = requests.post( self.webhook + "?event=ready", data=json.dumps( self.getData(), default=str ) )
                print( "Response:", r.content )
                sys.stdout.flush()


    def _reReadStatus( self ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            db.commit()
            cur = db.cursor()
            cur.execute( "SELECT status FROM jobs WHERE id=%s", ( self.id(), ) )
            self._data['status'] = cur.fetchOneDict()['status']


    def __getattr__(self, name):
        self.cacheIf()
        if name == 'status':
            if ( self.isValid() ):
                self._reReadStatus()
            if 'status' in self._data:  
                return self._data['status'].decode()
            else:
                return "PENDING"
        return super().__getattr__(name)


    def getDefaultData(self):
        dt = super().getDefaultData()
        dt['created'] = datetime.datetime.now()
        return dt


    def drop( self ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            db.cmd( "DELETE FROM jobfiles WHERE jobId=%s", [ self.id() ] )
            db.cmd( "DELETE FROM jobs WHERE id=%s", [ self.id() ] )


    def getSize( self ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            cur = db.cursor()
            cur.execute( "SELECT sum(size) AS s FROM jobfiles WHERE jobId=%s", ( self._id, ) )
            res = cur.fetchOneDict()['s']
            cur.reset()
            return res
        else:
            return 0;


    def getFileCount( self, status = '' ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            cur = db.cursor()
            if ( status == '' ):
                cur.execute( "SELECT count(*) AS c FROM jobfiles WHERE jobId=%s", ( self._id, ) )
            else:
                cur.execute( "SELECT count(*) AS c FROM jobfiles WHERE jobId=%s AND status=%s", ( self._id, status ) )
            res = cur.fetchOneDict()['c']
            cur.reset()
            return res
        else:
            return 0;


    def getNextFiles( self, status, count ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            cur = db.cursor()
            cur.execute( "SELECT * FROM jobfiles WHERE jobId=%s AND status=%s LIMIT %s", ( self._id, status, count ) )
            res = []
            row = cur.fetchOneDict()
            while ( row != None ):
                res.append( row )
                row = cur.fetchOneDict()
            return res
        else:
            return []
        
        


    def getFileSize( self, status = '' ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            cur = db.cursor()
            if ( status == '' ):
                cur.execute( "SELECT IFNULL(sum(size),0) AS c FROM jobfiles WHERE jobId=%s", ( self._id, ) )
            else:
                cur.execute( "SELECT IFNULL(sum(size),0) AS c FROM jobfiles WHERE jobId=%s AND status=%s", ( self._id, status ) )
            res = cur.fetchOneDict()['c']
            cur.reset()
            return res
        else:
            return 0;


    def getTapeCount( self ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            cur = db.cursor()
            cur.execute( "SELECT COUNT(DISTINCT tapeId) AS tc FROM jobfiles WHERE jobId=%s", ( self._id, ) )
            res = cur.fetchOneDict()['tc']
            cur.reset()
            return res
        else:
            return 0;


    def getData( self ):
        d = super().getData()
        if ( d['status'] == None ):
            d['status'] = 'PENDING'
        else:
            if isinstance( d['status'], bytearray ):
                d['status'] = ( d['status'] ).decode()
        d['size'] = self.getSize()
        d['filecount'] = self.getFileCount()
        d['tapecount'] = self.getTapeCount()
        d['fileready'] = self.getFileCount('RESTORED')
        d['filesizeready'] = self.getFileSize('RESTORED')
        return d
    

    def execute( self ):
        tc = FilelistBuilderThread( self )


    def clearFiles( self ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            db.cmd( "DELETE FROM jobfiles WHERE jobId=%s", [ self.id() ] )


    def updateStatus( self ):
        db = variables.getScopedDb()
        db.commit()
        cur = db.cursor()
        cur.execute( "SELECT DISTINCT status FROM jobfiles WHERE jobId=%s", ( self.id(), ) )
        statuslist = []
        st = cur.fetchOneDict()
        while st != None:
            statuslist.append( st['status'].decode() )
            st = cur.fetchOneDict()
        if len(statuslist)==2 and 'COPY' in statuslist and 'WAITING' in statuslist:
            self.status = 'TAPE OPERATIONS'
            self.save()
        elif len(statuslist)==1 and 'RESTORED' in statuslist:
            self.status = 'RESTORED'
            self.save()
        elif len(statuslist)==1 and 'DELETED' in statuslist:
            self.status = 'DELETED'
            self.save()
        elif len(statuslist)==2 and 'DELETED' in statuslist and 'KEPT' in statuslist:
            self.status = 'KEPT-DELETED'
            self.save()
        elif len(statuslist)==1 and 'KEPT' in statuslist:
            self.status = 'KEPT-DELETED'
            self.save()
        elif self.status != 'PAUSED' and len(statuslist)>1 and (('COPY' in statuslist) or ('RESTORED' in statuslist) ):
            self.status = 'RESTORING'
            self.save()


    def addFile( self, f, dstconfig ):
        if ( self.isValid() and f != None ):
            db = variables.getScopedDb()
            fsp = f.getFirstUsableFileSysPathStruct()
            if fsp != None:
                db.cmd( "INSERT INTO jobfiles (jobId, tapeId, fileId, srcpath, dstpath, dstfs, startblock, size, filecreationdate, status, created) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())",
                    (
                        self.id(), 
                        fsp['tape'].id(), 
                        None, #f.id(), 
                        fsp['srcpath'], 
                        "%s/%s/%s" % ( dstconfig['localpath'], self.username, fsp['vfspath'] ), 
                        dstconfig['localpath'],
                        f.getStartBlock( fsp['tape'] ), 
                        f.size,
                        f.created,
                        'WAITING',
                    ) 
                )
                return True
            else:
#               self.status = "TAPE-INACCESSIBLE"
                self.lasterror = "Source file not available: %s" % ( f.getFullPath() )
                self.save()
                return True
        else:
            raise Exception( "Cannot add file, job is not valid" )


    def isIdInList( self, id, list, idType ):
        for s in list:
            if ( s['data']['id'] == id and idType == s['type'] ):
                return True
        return False
    

    def buildFilelist( self ):
        if self.isValid():
            self.status = "FILELIST"
            self.save()
            src = json.loads( self.src )
            filelist = []
            stack = []
            for sel in src['sel']:
                type = sel['type']
                if ( type == 'file' ):
                    id = -1
                    if "id" in sel['data']:
                        id = sel['data']['id']
                        filelist.append( File( id ) )
                    if "path" in sel['data'] and "domain" in sel["data"]:
                        f = File.createByPathAndDomain( sel["data"]["path"], Domain.createByName( sel["data"]["domain"] ) )
                        if f:
                            filelist.append( f )

                if ( type == 'folder' ):
                    if "id" in sel["data"]: 
                        stack.append( Folder( sel['data']['id'] ) )
                    if "path" in sel["data"] and "domain" in sel["data"]:
                        fol = Folder.createByPathAndDomain( sel["data"]["path"], Domain.createByName( sel["data"]["domain"] ) )
                        if fol:
                            stack.append( fol )

            while len( stack ) > 0:
                folder = stack.pop()
                for f in folder.getSubFolders():
                    if ( not self.isIdInList( f.id(), src['unsel'], 'folder' ) ):
                        stack.append( f )
                for f in folder.getFiles():
                    if ( not self.isIdInList( f.id(), src['unsel'], 'file' ) ):
                        filelist.append( f )

            self.clearFiles()
            dstconfig = variables.getDestinationConfig( self.dststorage )
            ok = True
            for f in filelist:
                ok = ok and self.addFile( f, dstconfig )
            if ok:
                self.status = "WAITING"
                self.save()


    def sendDeleteWarning( self ):
        if ( self.webhook != None and self.webhook != "" ):
            print( "Sending delete warning to %s" % self.webhook )
            r = requests.post( self.webhook + "?event=deletewarning", data=json.dumps( self.getData(), default=str ) )
            if ( r.status_code == 200 ):
                return True
            else:
                return r


    def keep( self ):
        if ( self.status != "RESTORED" or not self.isValid() ):
            return False
        self.nexttask_sent = 0
        self.nexttask = datetime.datetime.now() + datetime.timedelta(days=7)
        self.save() 
        return True


    @staticmethod
    def getNextFilesForTape( tape, count=200 ):
        db = variables.getScopedDb()
        db.commit()
        cur = db.cursor()
        cur.execute( "SELECT jf.* FROM jobfiles AS jf " +
            "INNER JOIN jobs AS j ON (j.id=jf.jobId) " +
            "WHERE tapeId=%s AND " +
            "j.status IN ('RESTORING','WAITING','FREESPACE-STOP','TAPE OPERATIONS') AND " +
            "jf.status IN ('WAITING','COPY') " +
            "ORDER BY (j.status='FREESPACE-STOP'), j.id, startblock LIMIT %s", ( tape.id(), count ) )
        res = []
        while True:
            r = cur.fetchOneDict()
            if r == None:
                break
            res.append(r)
        cur.reset();
        return res


    @staticmethod
    def getNextFileForTape( tape ):
        db = variables.getScopedDb()
        db.commit()
        cur = db.cursor()
        cur.execute( "SELECT jf.* FROM jobfiles AS jf " +
            "INNER JOIN jobs AS j ON (j.id=jf.jobId) " +
            "WHERE tapeId=%s AND " +
            "j.status IN ('RESTORING','WAITING','FREESPACE-STOP','TAPE OPERATIONS') AND " +
            "jf.status IN ('WAITING','COPY') " +
            "ORDER BY (j.status='FREESPACE-STOP'), j.id, startblock LIMIT 1", ( tape.id(), ) )
        res = cur.fetchOneDict()
        cur.reset()
        return res;


    @staticmethod
    def updateJFStatus( jf, status, force=False ):
        if ( force ):
            db = variables.getScopedDb()
            db.commit()
            db.cmd( "UPDATE jobfiles SET status=%s, finished=now() WHERE id=%s", ( status, jf['id'] ) )
            job = Job( jf['jobId'] )
            job.updateStatus()
        else:
            _updatelog.append( { 'jf': jf, 'status': status } )
            if ( len( _updatelog ) > 100 ):
                Job.flushLog()


    @staticmethod
    def flushLog():
        db = variables.getScopedDb()
        db.commit()
        jobs = [];
        for up in _updatelog:
            db.cmd( "UPDATE jobfiles SET status=%s, finished=now() WHERE id=%s", ( up['status'], up['jf']['id'] ) )
            if up['jf']['jobId'] not in jobs:
                jobs.append( up['jf']['jobId'] )
        for j in jobs:
            job = Job( j )
            job.updateStatus()
        _updatelog.clear()


    @staticmethod
    def mkPath( path ):
        try:
            path = path.split("/")
            path = path[:-1]
            ppart = "/"
            for p in path:
                if p != "":
                    ppart = os.path.join( ppart, p )
                    if not os.path.exists( ppart ):
                        os.mkdir( ppart )
        except:
            print( "Directory not created: %s" % path )
            pass


    @staticmethod
    def copyJF( jf ):
        Job.updateJFStatus( jf, 'COPY' )
        if not os.path.exists( jf['dstpath'] ):
            Job.mkPath( jf['dstpath'] )
#            print( jf['srcpath'] + " -> " + jf['dstpath'] )
            try:
                shutil.copy2( jf['srcpath'], jf['dstpath'] )
            except:
                pass
        Job.updateJFStatus( jf, 'RESTORED' )


