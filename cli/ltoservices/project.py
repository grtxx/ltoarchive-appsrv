
from ltoservices.baseservice import BaseService

class projectService(BaseService):

    def check( self, domain, wn ):
        data = self.LTO.sendRequest('GET', "/api/v1/domain/%s/%s/getinfo" % ( domain, wn ) )
        if ( data["status"] == 200 ):
            return data["data"]["data"]
        else:
            return None
