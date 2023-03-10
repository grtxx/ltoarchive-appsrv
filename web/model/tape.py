import model.variables as variables
from sqlalchemy import ForeignKey, Column, String, Integer, Boolean
from typing import Optional

class Tape(variables.Declarative_Base):
    __tablename__ = variables.TablePrefix + 'Tape'
    id = Column( Integer, primary_key=True)
    label = Column( String(length=100) )
    role = Column( Integer )
    isAvailable = Column( Boolean )
    isActive = Column( Boolean, default=True)
    parentTape = Column( Integer, ForeignKey( column=variables.TablePrefix + 'Tape.id' ) )
