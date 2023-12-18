#!/bin/python3

import os
import tornado
import tornado.ioloop
from tornado.web import Application
from tornado.web import StaticFileHandler
from ltoapi import LTOApi
import requests

def main():
    app = Application(
        ( 
            ( r'/api/v1/(.*)', LTOApi ),
            ( r"/(.*)", StaticFileHandler, {"path": os.path.join( os.path.dirname( os.path.realpath(__file__) ), "static" ), "default_filename": "index.html" } ),
        )
    )

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen( 8000 )
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

    #from model.folder import Folder

    #print( "FOLDER" )
    #f = Folder(126622)
    #print( f.getFullPath() )
    #f.dropUnlinkedFiles()
    #print( "OK" )