#!/usr/bin/python3.6m

from ltoarchive import LTOArchive

server = "http://10.21.19.150:8000"

LTO = LTOArchive( server )

LTO.archivedomain.create( "COMPACT_TV" )
print( LTO.archivedomain.list() )

