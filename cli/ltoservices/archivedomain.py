import json
from ltoservices.baseservice import BaseService


class archivedomainService(BaseService):

    def list( self ):
        data = self.LTO.sendRequest('GET', "/api/v1/archivedomain/list" )
        if ( data["status"] == 200 ):
            return data["data"]["data"]
        else:
            return None

    def create( self, name ):
        dt = { 'name': name }
        data = self.LTO.sendRequest( 'PUT', "/api/v1/archivedomain/new", data=dt )
        return data["status"]