
from ltoservices.baseservice import BaseService

class tapeService(BaseService):

    def list( self ):
        data = self.LTO.sendRequest('GET', "/api/v1/tape/list" )
        if ( data["status"] == 200 ):
            return data["data"]["data"]
        else:
            return None
