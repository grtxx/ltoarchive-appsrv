import model.variables as variables
from model.app import App
from model.baseentity import BaseEntity
import uuid
import datetime
import hashlib
import base64

class Session(BaseEntity):
    _tablename = variables.TablePrefix + 'sessions'
    _fields = ( 'sessionId', 'userId', 'lastseen' )


    @staticmethod
    def appAuth( token, queryGuid, signature ):
        s = Session()
        s.sessionId = token
        if s.auth( queryGuid, signature ):
            return s
        return None


    @staticmethod
    def createByToken( token ):
        s = Session()
        s.sessionId = token
        return s


    def __init__( self ):
        super().__init__()
        self.sessionId = ""


    def getAppByToken( self, token ):
        return App.createByAccessToken( token )


    def auth( self, queryGuid, signature ):
        app = self.getAppByToken( self.sessionId )
        if app:
            sha = hashlib.sha1()
            sha.update( ( '%s--%s' % ( queryGuid, app.appSecret.decode('UTF-8') ) ).encode('ascii') )
            calculatedSignature = base64.b64encode( sha.digest() ).decode( 'ascii' ) 
            print( calculatedSignature )
            if signature == calculatedSignature:
                self.userId = App.getUserIdForAccessToken( self.sessionId )
                return True
        return False


    def getDefaultData( self ):
        dt = super().getDefaultData()
        dt["sessionId"] = uuid.uuid4()
        dt["lastseen"] = datetime.time()
        dt["userId"] = None
        return dt

