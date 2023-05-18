
from ltoservices.baseservice import BaseService

class tapeService(BaseService):

    def list( self ):
        data = self.LTO.sendRequest('GET', "/api/v1/tape/list" )
        if ( data["status"] == 200 ):
            return data["data"]["data"]
        else:
            return None


    def create( self, label, copyNumber ):
        dt = { 'label': label, 'copyNumber': copyNumber }
        data = self.LTO.sendRequest( 'PUT', "/api/v1/tape/new", data=dt )
        return data["data"]["data"]


    def updateContent( self, label ):
        dt = {}
        data = self.LTO.sendRequest( 'PATCH', "/api/v1/tape/%s/updatecontent" % ( label ), data=dt )
        return data["data"]
