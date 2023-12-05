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

class Job(BaseEntity):
    _tablename = variables.TablePrefix + 'jobs'
    _fields = [ 'email', 'username', 'src', 'dststorage', 'created', 'status', 'nexttask', 'webhook' ]
    _orderField = "created DESC"


    def __init__( self, id = 0 ):
        super().__init__( id )
        

    def __setattr__(self, name: str, value: Any) -> None:
        if name == 'status':
            if self.status != value:
                if value=='RESTORED':
                    self.finished=datetime.datetime.now()
        super().__setattr__(name, value)
        if name == 'status':
            if ( self.webhook != None and self.webhook != "" ):
                r = requests.post( self.webhook, data=json.dumps( self.getData() ) )


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
            d['status'] = "%s" % ( d['status'] ).decode( 'UTF-8' )
        d['size'] = self.getSize()
        d['filecount'] = self.getFileCount()
        d['tapecount'] = self.getTapeCount()
        d['fileready'] = self.getFileCount('RESTORED')
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
        if len(statuslist)==1 and 'RESTORED' in statuslist:
            self.status = 'RESTORED'
            self.save()
        elif len(statuslist)>1 and (('COPY' in statuslist) or ('RESTORED' in statuslist) ):
            self.status = 'RESTORING'
            self.save()


    def addFile( self, f, dstconfig ):
        if ( self.isValid() and f != None ):
            db = variables.getScopedDb()
            fsp = f.getFirstUsableFileSysPathStruct()
            db.cmd( "INSERT INTO jobfiles (jobId, tapeId, fileId, srcpath, dstpath, startblock, size, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    self.id(), 
                    fsp['tape'].id(), 
                    f.id(), 
                    fsp['srcpath'], 
                    "%s/%s/%s" % ( dstconfig['localpath'], self.username, fsp['vfspath'] ), 
                    f.getStartBlock( fsp['tape'] ), 
                    f.size,
                    'WAITING',
                ) 
            )
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
            for f in filelist:
                self.addFile( f, dstconfig )
            self.status = "WAITING"
            self.save()


    @staticmethod
    def getNextFileForTape( tape ):
        db = variables.getScopedDb()
        cur = db.cursor()
        cur.execute( "SELECT * FROM jobfiles WHERE tapeId=%s AND status IN ('WAITING','COPY') ORDER BY jobId, startblock LIMIT 1", ( tape.id(), ) )
        return cur.fetchOneDict()

    
    @staticmethod
    def updateJFStatus( jf, status ):
        db = variables.getScopedDb()
        db.cmd( "UPDATE jobfiles SET status=%s WHERE id=%s", ( status, jf['id'] ) )
        job = Job( jf['jobId'] )
        job.updateStatus()


    @staticmethod
    def mkPath( path ):
        try:
            path = path.split("/")
            path = path[:-1]
            ppart = "/"
            for p in path:
                ppart = os.path.join( ppart, p )
                if not os.path.exists( ppart ):
                    os.mkdir( ppart )
        except:
            pass


    @staticmethod
    def copyJF( jf ):
        Job.updateJFStatus( jf, 'COPY' )
        if not os.path.exists( jf['dstpath'] ):
            Job.mkPath( jf['dstpath'] )
            #print( jf['srcpath'] + " -> " + jf['dstpath'] )
            try:
                shutil.copy( jf['srcpath'], jf['dstpath'] )
            except:
                pass
        Job.updateJFStatus( jf, 'RESTORED' )
