#!/usr/bin/python3.6m

import sys
import re
from ltoarchive import LTOArchive



class Settings:
    def __init__( self ):
        self.settings = []
        self.commands = []
        self.cmdlineopts = [
            { "short": "s", "long": "server", "default": "http://127.0.0.1" },
            { "short": "p", "long": "port", "default": "8000" },
            { "short": "n", "long": "copynumber", "default": "0" }
        ]
        self.parseArgs()

    def get( self, name ):
        if name in self.settings:
            return self.settings[ name ]
        else:
            return ""
        
    def getCommand( self, num ):
        if num < len( self.commands ):
            return self.commands[num]
        else:
            return ""

    def parseArgs( self ):
        self.settings = {}
        self.commands = []
        i = 1
        for p in self.cmdlineopts:
            if "default" in p:
                self.settings[ p["long"] ] = p["default"]
        while i < len( sys.argv ):
            if ( sys.argv[i][:1] == "-" ):
                for p in self.cmdlineopts:
                    if ( sys.argv[i] == "-%s" % p["short"] ):
                        if ( i + 1 < len( sys.argv ) ):
                            self.settings[ p["long"] ] =  sys.argv[i+1]
                        i = i + 1
                    grps = re.match( r"--%s=(.*)$" % p["long"], sys.argv[i] )
                    if ( grps ):
                        self.settings[ p["long"] ] = grps.groups(1)[0]
            else:
                self.commands.append( sys.argv[i] )
            i = i + 1
        pass



def domainCommands( settings ):
    LTO = LTOArchive( "%s:%s" % ( settings.get("server"), settings.get("port") ) )
    if settings.getCommand(1) == "list":
        print( LTO.domain.list() )

    if settings.getCommand(1) == "create":
        if settings.getCommand(2) != "":
            print( LTO.domain.create( settings.getCommand(2) ) )

    if settings.getCommand(1) == "drop":
        if settings.getCommand(2) != "":
            print( LTO.domain.drop( settings.getCommand(2) ) )


def tapeCommands( settings ):
    LTO = LTOArchive( "%s:%s" % ( settings.get("server"), settings.get("port") ) )
    if settings.getCommand(1) == "list":
        print( LTO.tape.list() )

    if settings.getCommand(1) == "add":
        if settings.getCommand(2) != "" and settings.get('copynumber') != "":
            print( LTO.tape.create( settings.getCommand(2), settings.get('copynumber') ) )

    if settings.getCommand(1) == "updatecontent":
        print( LTO.tape.updateContent( settings.getCommand(2) ) )


def router():
    settings = Settings()
    if ( settings.getCommand(0) == "domain" ):
        domainCommands( settings )
    if ( settings.getCommand(0) == "tape" ):
        tapeCommands( settings )


router()





#LTO.archivedomain.create( "COMPACT_TV" )
#print( LTO.archivedomain.list() )

#print( LTO.content.getFolder( "UMBRELLA", "/tmp-2023-02/valami" ) )