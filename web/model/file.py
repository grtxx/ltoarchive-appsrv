import model.variables as variables
from sqlalchemy import ForeignKey, Column, String, Integer, Boolean, BigInteger, DateTime, VARBINARY
from typing import Optional

class File(variables.Declarative_Base):
    __tablename__ = variables.TablePrefix + 'File'
    id = Column( Integer, primary_key=True)
    archiveDomain = Column( Integer, ForeignKey( column=variables.TablePrefix + 'ArchiveDomain.id' ) )
    name = Column( String(length=250), index=True )
    ext = Column( String(length=32), index=True )
    size = Column( BigInteger, index=True )
    created = Column( DateTime, index=True )
    isDeleted = Column( Boolean, default=False, index=True )
    isLatest = Column( Boolean, default=False, index=True )
    hash = Column( VARBINARY, index=True )
    vuuid = Column( VARBINARY, index=True )
    partation = Column( BigInteger, index=True )
    startBlock = Column( BigInteger, index=True )
    parentFolder = Column( Integer, ForeignKey( column=variables.TablePrefix + 'Folder.id' ) )

