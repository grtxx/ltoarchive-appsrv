import model.variables as variables
from sqlalchemy import ForeignKey, Column, Unicode, Integer, Boolean, BigInteger, DateTime, VARBINARY
from typing import Optional
from sqlalchemy.orm import relationship
import xattr
import os

class File2Tape(variables.Base):
    __tablename__ = variables.TablePrefix + 'File2Tape'
    id = Column( Integer, primary_key=True)
    fileId = Column( Integer, ForeignKey( column=variables.TablePrefix + 'File.id' ) )
    tapeId = Column( Integer, ForeignKey( column=variables.TablePrefix + 'Tape.id' ) )
    vuuid = Column( Unicode(32), index=True )
    partation = Column( BigInteger, index=True )
    startBlock = Column( BigInteger, index=True )

    filerecord = relationship( "File", back_populates="copies" )
    tape = relationship( "Tape", back_populates="files" )


    @staticmethod
    def createByFileAndTape( file, tape, session=None ):
        if ( session == None ):
            session = variables.getScopedSession()
        t = session.query(File2Tape).filter( File2Tape.tape==tape, File2Tape.filerecord==file ).first()
        if t:
            return t
        else:
            return File2Tape( filerecord=file, tape=tape )


    def getFSPath( self ):
        return os.path.join( variables.LTFSRoot, self.tape.label, self.filerecord.archiveDomain.name, self.filerecord.getFullPath() )


    def updateMeta( self ):
        fspath = self.getFSPath()
        try:
            self.startBlock = int( xattr.getxattr( fspath, variables.vea_pre + 'ltfs.startblock' ) )
            self.partation = int( xattr.getxattr( fspath, variables.vea_pre + 'ltfs.partation' ) )       
        except:
            if ( self.startBlock == 0 ):
                print( "ERROR" )
            pass

