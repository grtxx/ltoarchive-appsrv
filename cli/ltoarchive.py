import pycurl
import re
import json
from io import BytesIO
from ltoservices.tape import tapeService
from ltoservices.domain import domainService
from ltoservices.content import contentService
from ltoservices.project import projectService


class LTOArchive():

    def __init__( self, server ):
        self.server = server
        self.key= ""
        self.tape = tapeService( self )
        self.domain = domainService( self )
        self.content = contentService( self )
        self.project = projectService( self )

    
    def sendRequest( self, method, uri, data=None, filedata=None ):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt( c.URL, "%s%s" % ( self.server, uri ) );
        if method == 'POST':
            c.setopt( c.POST, True );
            c.setopt( c.HTTPHEADER, [ 'Content-Type: multipart/form-data' ] );
            if data:
                c.setopt( c.POSTFIELDS, data );
        elif method == 'PATCH' or method == 'PUT' or method == "DELETE":
            c.setopt( c.CUSTOMREQUEST, method );
            c.setopt( c.POSTFIELDS, json.dumps( data ) );
        elif method == 'GET':
            pass
#           c.setopt( c.URL, "%s%s" % ( self.server, uri ) );

        c.setopt( c.HTTPHEADER, [ 'X-AccessKey: %s' % ( self.key ) ] );
        #c.setopt( c..RETURNTRANSFER, true );
        c.setopt( c.VERBOSE, 0 );
        c.setopt( c.HEADER, 1 );
        c.setopt( c.WRITEDATA, buffer )
        c.setopt( c.SSL_VERIFYPEER, 1 )
        c.setopt( c.SSL_VERIFYHOST, 2 )
        if filedata:
            for f in filedata.keys():
                c.setopt( c.HTTPPOST, [ ( f, ( c.FORM_FILE, filedata[f] ) ) ] )
        c.perform();
        c.close();

        ret = buffer.getvalue().decode().replace( "\r", "" ).split( "\n" )
        ret2 = "";
        mode = 0;
        datamode = 1;
        if method == "POST":
            datamode = 2;
        status = -1;

#        print( "-----------------" )
#        print( "%s> %s" % ( method, uri ) )
#        print( "-----------------" )
        for r in ret:
            #print( r )
            m = re.match( r'^(HTTP|SPDY)\/([0-9\.]+)\s(\d+) .*', r )
            if m and mode == ( datamode - 1 ):
                status = int( m.groups(0)[2] )

            if r == "":
                mode = mode + 1

            if mode == datamode and r != "":
                ret2 += "%s\n" % r;

        ret3 = ""
        try:
#            print( ret2 )
            ret3 = json.loads( ret2 )
        except:
            print( "JSON parse hiba: " )
            print( ret2 )
            print( "----------------" )
            ret3 = ""
            status = 500

        self.lastResult = {
                'status': status,
                'data': ret3,
                'raw': ret2
        }
        return self.lastResult;
