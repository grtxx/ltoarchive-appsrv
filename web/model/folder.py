import model.variables as variables
import sqlalchemy
from sqlalchemy import ForeignKey, Index, Column, Unicode, Integer, Boolean, BigInteger, DateTime
from sqlalchemy.orm import relationship
from typing import Optional


class Folder(variables.Base):
    __tablename__ = variables.TablePrefix + 'Folder'
    id = Column( Integer, primary_key=True)
    archiveDomainId = Column( Integer, ForeignKey( column=variables.TablePrefix + 'ArchiveDomain.id' ), nullable = False )
    name = Column( Unicode(250, collation='utf8_general_ci'), index=True )
    size = Column( BigInteger, index=True )
    created = Column( DateTime, index=True )
    isDeleted = Column( Boolean, default=False, index=True )
    parentFolderId = Column( Integer, ForeignKey( column=variables.TablePrefix + 'Folder.id' ), nullable = True )

    parentFolder = relationship( "Folder", backref="folders", remote_side=[id] )
    archiveDomain = relationship( "ArchiveDomain", back_populates="folders" )
    files = relationship( "File", back_populates="parentFolder" )

    fullPath = ""

    @staticmethod
    def createFolder( domain, parentFolder, name ):
        session = variables.getScopedSession()
        f = session.query(Folder).filter( Folder.parentFolder==parentFolder, Folder.name==name, Folder.archiveDomain==domain ).first();
        if f:
            return f
        else:
            folder = Folder( archiveDomain=domain, name=name, parentFolder=parentFolder )
            return folder
    

    def getFullPath( self ):
        if ( self.fullPath == "" ):
            path = self.name
            pf = self
            while pf:
                pf = pf.parentFolder
                if pf:
                    path = pf.name + "/" + path
            self.fullPath = path
            return path
        else:
            return self.fullPath;