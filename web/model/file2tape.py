import model.variables as variables
from sqlalchemy import ForeignKey, Column, String, Integer, Boolean, BigInteger, DateTime
from typing import Optional

class File2Tape(variables.Declarative_Base):
    __tablename__ = variables.TablePrefix + 'File2Tape'
    id = Column( Integer, primary_key=True)
    fileId = Column( Integer, ForeignKey( column=variables.TablePrefix + 'File.id' ) )
    tapeId = Column( Integer, ForeignKey( column=variables.TablePrefix + 'Tape.id' ) )
