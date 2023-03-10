import model.variables as variables
from sqlalchemy import ForeignKey, Index, Column, String, Integer, Boolean, BigInteger, DateTime
from typing import Optional

class Folder(variables.Declarative_Base):
    __tablename__ = variables.TablePrefix + 'Folder'
    id = Column( Integer, primary_key=True)
    archiveDomain = Column( Integer, ForeignKey( column=variables.TablePrefix + 'ArchiveDomain.id' ) )
    name = Column( String(length=250), index=True )
    size = Column( BigInteger, index=True )
    created = Column( DateTime, index=True )
    isDeleted = Column( Boolean, default=False, index=True )
    parentFolder = Column( Integer, ForeignKey( column=variables.TablePrefix + 'Folder.id' ) )
