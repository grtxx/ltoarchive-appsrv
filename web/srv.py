#!/bin/python3

import os
import tornado
import tornado.ioloop
from tornado.web import Application
from tornado.web import StaticFileHandler
import sqlalchemy
from tornado_sqlalchemy import SQLAlchemy 
from ltoapi import LTOApi
import model.variables as variables
import dbmodel


def main():
    dbmodel.createAll()

    Session = sqlalchemy.orm.sessionmaker()
    Session.configure(bind=variables.DBEngine)
    Session = Session()

    app = Application(
        ( 
            ( r'/api/v1/(.*)', LTOApi, { "session": Session } ),
            ( r"/(.*)", StaticFileHandler, {"path": os.path.join( os.path.dirname( os.path.realpath(__file__) ), "static" ), "default_filename": "index.html" } ),
        )
    )

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen( 8000 )
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()