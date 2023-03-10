
import model.variables as variables
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base


class ArchiveDomain(variables.Declarative_Base):
    __tablename__ = variables.TablePrefix + 'ArchiveDomain'
    id = Column( Integer, primary_key=True)
    name = Column( String(length=100), index=True )
    backupCount = Column( Integer, default=1 )
    isExclusiveOnTapes = Column( Boolean, default=False )
    isActive = Column( Boolean, default=True )

