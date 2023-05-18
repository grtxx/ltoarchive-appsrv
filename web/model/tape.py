import model.variables as variables
from sqlalchemy import ForeignKey, Column, Unicode, Integer, Boolean
import threading
import os
from model.archivedomain import ArchiveDomain
from model.file2tape import File2Tape
from sqlalchemy.orm import relationship
import model.file as File



class Tape(variables.Base):
    __tablename__ = variables.TablePrefix + 'Tape'
    id = Column( Integer, primary_key=True)
    label = Column( Unicode(length=8, collation='utf8_general_ci') )
    copyNumber = Column( Integer, index=True )
    isAvailable = Column( Boolean )
    isActive = Column( Boolean, default=True)
    parentTape = Column( Integer, ForeignKey( column=variables.TablePrefix + 'Tape.id' ) )

    files = relationship( "File2Tape", back_populates="tape" )


    @staticmethod
    def createByName( name, session=None ):
        if ( session == None ):
            session = variables.getScopedSession()
        t = session.query(Tape).filter( Tape.label==name ).first();
        if t:
            return t
        else:
            return None


    def getRoot( self ):
        return os.path.join( variables.LTFSRoot, self.label )


    def updateContent( self ):
        cartRoot = os.listdir( self.getRoot() )
        domains = []
        for d in cartRoot:
            if ( os.path.isdir( os.path.join( self.getRoot(), d ) ) ):
                domains.append( d )
        for d in domains:
            self.updateDomainContent( d )


    def updateDomainContent( self, d ):
        session = variables.getScopedSession()
        session.query(File2Tape).filter(File2Tape.tape==self).delete()
        domain = ArchiveDomain.createByName( d, session=session )
        root = os.path.join( self.getRoot(), d )
        stack = [ "" ]
        while len(stack) > 0:
            dir = stack.pop()
            print( "%s - %s" % ( domain.name, dir ) )
            files = os.listdir( os.path.join( root, dir ) )
            afolder = domain.getFolder( dir )
            for f in files:
                if os.path.isfile( os.path.join( root, dir, f ) ):
                    hash = File.genHash( os.path.join( root, dir, f ) )
                    domain.addFileRecord( afolder, f, self.id, hash )
                    pass
                else:
                    domain.addFolder( afolder, f )
                    stack.append( os.path.join( dir, f ) )
            session.commit()

