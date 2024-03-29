from typing import Any
import model.variables as variables
import datetime
from model.baseentity import BaseEntity
from model.file import File
from model.folder import Folder
import json
import os
import shutil
import requests
import sys

class Job(BaseEntity):
    _tablename = variables.TablePrefix + 'jobs'
    _fields = [ 'email', 'username', 'src', 'dststorage', 'created', 'finished', 'status', 'nexttask', 'webhook' ]
    _orderField = "created DESC"


    def __init__( self, id = 0 ):
        super().__init__( id )
        

    def __setattr__(self, name: str, value: Any) -> None:
        if name == 'status':
            if self.status != value:
                if value=='RESTORED':
                    self.finished=datetime.datetime.now()
        super().__setattr__(name, value)
        if name == 'status' and value == 'RESTORED':
            if ( self.webhook != None and self.webhook != "" ):
                r = requests.post( self.webhook + "?event=ready", data=json.dumps( self.getData(), default=str ) )
                print( "Response:", r.content )
                sys.stdout.flush()


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
            return cur.fetchOneDict()['s']
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
            return cur.fetchOneDict()['c']
        else:
            return 0;


    def getFileSize( self, status = '' ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            cur = db.cursor()
            if ( status == '' ):
                cur.execute( "SELECT IFNULL(sum(size),0) AS c FROM jobfiles WHERE jobId=%s", ( self._id, ) )
            else:
                cur.execute( "SELECT IFNULL(sum(size),0) AS c FROM jobfiles WHERE jobId=%s AND status=%s", ( self._id, status ) )
            return cur.fetchOneDict()['c']
        else:
            return 0;


    def getTapeCount( self ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            cur = db.cursor()
            cur.execute( "SELECT COUNT(DISTINCT tapeId) AS tc FROM jobfiles WHERE jobId=%s", ( self._id, ) )
            return cur.fetchOneDict()['tc']
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
    

    def clearFiles( self ):
        if ( self.isValid() ):
            db = variables.getScopedDb()
            db.cmd( "DELETE FROM jobfiles WHERE jobId=%s", [ self.id() ] )


    def updateStatus( self ):
        db = variables.getScopedDb()
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
        elif len(statuslist)>1 and (('COPY' in statuslist) or ('RESTORED' in statuslist) ):
            self.status = 'RESTORING'
            self.save()


    def addFile( self, f, dstconfig ):
        if ( self.isValid() and f != None ):
            db = variables.getScopedDb()
            fsp = f.getFirstUsableFileSysPathStruct()
            if fsp != None:
                db.cmd( "INSERT INTO jobfiles (jobId, tapeId, fileId, srcpath, dstpath, dstfs, startblock, size, status, created) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now())",
                    (
                        self.id(), 
                        fsp['tape'].id(), 
                        None, #f.id(), 
                        fsp['srcpath'], 
                        "%s/%s/%s" % ( dstconfig['localpath'], self.username, fsp['vfspath'] ), 
                        dstconfig['localpath'],
                        f.getStartBlock( fsp['tape'] ), 
                        f.size,
                        'WAITING',
                    ) 
                )
                return True
            else:
                self.status = "TAPE-INACCESSIBLE"
                self.save()
                return False
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
                    id = sel['data']['id']
                    filelist.append( File( id ) )
                if ( type == 'folder' ):
                    stack.append( Folder( sel['data']['id'] ) )

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


    @staticmethod
    def getNextFileForTape( tape ):
        db = variables.getScopedDb()
        cur = db.cursor()
        cur.execute( "SELECT jf.* FROM jobfiles AS jf " +
            "INNER JOIN jobs AS j ON (j.id=jf.jobId) "
            "WHERE tapeId=%s AND j.status IN ('RESTORING','WAITING') AND jf.status IN ('WAITING','COPY') ORDER BY j.id, startblock LIMIT 1", ( tape.id(), ) )
        return cur.fetchOneDict()


    @staticmethod
    def updateJFStatus( jf, status ):
        db = variables.getScopedDb()
        db.cmd( "UPDATE jobfiles SET status=%s, finished=now() WHERE id=%s", ( status, jf['id'] ) )
        job = Job( jf['jobId'] )
        job.updateStatus()


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
