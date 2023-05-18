
from ltoservices.baseservice import BaseService

class contentService(BaseService):

    def getFolder( self, arcDomain, path ):
        data = self.LTO.sendRequest('GET', "/api/v1/content/%s/getfolder%s" % ( arcDomain, path ) )
        if ( data["status"] == 200 ):
            return data["data"]["data"]
        else:
            return None
