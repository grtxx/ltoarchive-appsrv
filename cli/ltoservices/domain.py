import json
from ltoservices.baseservice import BaseService


class domainService(BaseService):

    def list( self ):
        data = self.LTO.sendRequest('GET', "/api/v1/domain/list" )
        if ( data["status"] == 200 ):
            return data["data"]["data"]
        else:
            return None

    def create( self, name ):
        dt = { 'name': name }
        data = self.LTO.sendRequest( 'PUT', "/api/v1/domain/new", data=dt )
        return data["status"]
    
    def drop( self, name ):
        data = self.LTO.sendRequest( 'DELETE', "/api/v1/domain/%s" % name )
        return data
    
