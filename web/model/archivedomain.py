
import model.variables as variables
from model.folder import Folder
from model.file import File
from model.file2tape import File2Tape
from sqlalchemy import Column, Unicode, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker, scoped_session

class ArchiveDomain(variables.Base):
    __tablename__ = variables.TablePrefix + 'ArchiveDomain'
    id = Column( Integer, primary_key=True)
    name = Column( Unicode(length=100, collation='utf8_bin'), index=True )
    backupCount = Column( Integer, default=1 )
    isExclusiveOnTapes = Column( Boolean, default=False )
    isActive = Column( Boolean, default=True )
    copyCount = Column( Integer, default=2 )

    folders = relationship( "Folder", back_populates="archiveDomain" )
    files = relationship( "File", back_populates="archiveDomain" )

    @staticmethod
    def createByName( name, session=None ):
        if ( session==None ):
            session = variables.getScopedSession()
        domain = session.query(ArchiveDomain).filter( ArchiveDomain.name==name ).first()
        if ( not domain ):
            domain = ArchiveDomain( name = name )
            session.add( domain )
            session.commit()
        return domain


    def getFolder( self, path ):
        path = path.split("/")
        list = self.folders
        afolder = None
        for p in path:
            if ( p != "" ):
                for l in list:
                    if ( l.name == p ):
                        list = l.folders;
                        afolder = l
                        break;
        return afolder

    def addFolder( self, parentFolder, name ):
        return Folder.createFolder( self, parentFolder, name )


    def addFileRecord( self, parentFolder, name, tapeId, hash ):
        from model.tape import Tape
        session = variables.getScopedSession()
        tape = session.query( Tape ).filter( Tape.id==tapeId ).first()
        file = File.createFile( self, parentFolder, name, hash )
        file.addCopy( tape )
        return file
    

    def kill( self ):
        session = variables.getScopedSession()
        session.query(File2Tape).filter(File2Tape.filerecord.archiveDomain==self).delete()
        session.query(File).filter(File.archiveDomain==self).delete()
        session.query(Folder).filter(Folder.archiveDomain==self).delete()
        session.query(ArchiveDomain).filter(ArchiveDomain==self).delete()
