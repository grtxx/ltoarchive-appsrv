
class ApiService_base:
    _apiServer: None

    def getRoutes():
        return []
    

    def registerApiServer( self, srv ):
        self._apiServer = srv;
