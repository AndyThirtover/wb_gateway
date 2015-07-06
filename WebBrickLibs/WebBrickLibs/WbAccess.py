# Copyright L.P.Klyne 2013 
# Licenced under 3 clause BSD licence 

# $Id: WbAccess.py 2612 2008-08-11 20:08:49Z graham.klyne $
#
"""
Functions for accessing WebBricks
"""

import httplib
import socket
import StringIO

from MiscLib.DomHelpers import parseXmlString
from MiscLib.Logging    import Trace, Info, Warn, Error

# we no longer need a 2 second timeout
HTTP_TIMEOUT    = 10

def GetHTTPXmlDom(adrs,uri):
    """
    Return content of an HTTP resource as an XML DOM object.    
    """
    xmlstr = GetHTTPData(adrs, uri)
#    return parseXmlString(xmlstr)
# alternative
    if xmlstr:
        try:
            return parseXmlString(xmlstr)
        except Exception, ex:
            #
            Warn("XML error %s : (%s,%s) %s " % (ex, adrs,uri, xmlstr) ,"WebBrickLibs.WbAccess.GetHTTPXmlDom")
    return None

def GetHTTPLines(adrs,uri):
    """
    Return content of an HTTP resource as a sequence lines (including 
    terminating newlines), or None if the resource cannot be read.
    """
    data = GetHTTPData(adrs,uri)
    return data and StringIO.StringIO(data).readlines()

def GetHTTPData(adrs,uri):
    """
    Return content of an HTTP resource as a single string.
    """
    #TODO: raise exception on error? (cf. SendHTTPCmd)
    r = DoHTTPRequest(adrs,"GET",uri)
    if r and (r.status != 200):
        Warn("%s HTTP error %u(%s)" %(adrs,r.status,r.reason),
                "WebBrickLibs.WbAccess.GetHTTPLines")
        return None
    return r and r.read()

def SendHTTPCommands(adrs,commands):
    """
    Send supplied command data to a WebBrick using a series of HTTP operations
    """
    for cmd in commands:
        if (cmd[0] != '#') :
            # sys.stdout.write(".")
            SendHTTPCmd(adrs,cmd)
    return

def SendHTTPCmd(adrs,cmd):
    """
    Send a command to a WebBrick via an HTTP transaction.

    This function precedes and follows the command with a colon (:), 
    and encodes it in a URI, with %-encoding applied as necessary.
    
    If the command succeeds, the HTTP transaction handle is returned;  this 
    can be interrogated by the calling program to determine additional information
    about the transaction.  If the command fails, an exception is raised.
    """
    # Assemble URI
    uri = "/hid.spi?com=%3A"
    for c in cmd:
        if isUriUnreserved(c):
            uri = uri + c
        else:
            uri = uri + "%" + MakeHex(c,2)
    uri = uri + "%3A"
    # Do request
    req = DoHTTPRequest(adrs,"GET",uri)
    msg = None
    if not req:
        msg = "Null response from DoHTTPRequest"
    if msg or (req.status not in [200,302]):
        msg = msg or "HTTP error "+str(req.status)+": "+req.reason
        Warn(msg, "WebBrickLibs.WbAccess.SendHTTPCmd")
        raise WbAccessException(msg)
    return req

def DoHTTPRequest(adrs, cmd, uri):
    """
    Execute an HTTP request using the specified host, command and uri path,
    and return the corresponding response object, or None if the request fails.
    """
    #Trace("HTTP to %s, %s %s" % (adrs, cmd, uri), "WebBrickLibs.WbAccess.WbAccess" )
    h = HTTPTimeoutConn(adrs)       # Connection with 2-second response timeout
    try:
        try:
            h.request( cmd, uri )
        except socket.error, msg:
            Warn("Socket open failure: %s (%s/%s)"%(msg,adrs,uri),
                    "WebBrickLibs.WbAccess.DoHTTPRequest")
            
            if str(msg) == "timed out": raise HTTPTimeout()
            raise WbAccessException("DoHTTPRequest: Addrees: %s Error: %s" % (adrs,msg) )
        txtlines = h.getresponse()
    except Exception,e :
        # what would the stacktrace look like?
        Warn("Get Response Failure: %s (%s/%s)"%(cmd,adrs,uri),
                    "WebBrickLibs.WbAccess.DoHTTPRequest")
        raise
    finally:
        h.close()
    return txtlines

def isUriUnreserved(c):
    return ( c.isalpha() or c.isdigit() or (c in "-_.~") )

def isUriReserved(c):
    return (c in (":/?#[]@"+"!$&'()*+,;="))     # gendelims + subdelims

def MakeHex(char, length):
    # From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/82748
    # hex representation of character/integer
    char = ord(char)
    x    = hex(char)[2:]
    while len(x) < length:
        x = '0' + x
    return x


# HTTP connection with request timeout
#    
# Code provided by Robert Brewer
# http://groups.google.com/group/cherrypy-users/browse_frm/thread/f0e6f9cbd3b65b0c/953fe5ef58fcc5fd#953fe5ef58fcc5fd
class HTTPTimeoutConn(httplib.HTTPConnection):
    """
    Subclass of httplib.HTTPConnection that imposes a 2-second timeout on all connections.
    This reduces the extent to which absent WebBricks can cause resources to be hogged.
    """
    
    def connect(self):
        """Connect to the host and port specified in __init__."""
        msg = "getaddrinfo returns an empty list"
        for res in socket.getaddrinfo(self.host, self.port, 0,
                                      socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.sock = socket.socket(af, socktype, proto)
                # Set a timeout on the socket
                self.sock.settimeout( HTTP_TIMEOUT )
                if self.debuglevel > 0:
                    print "connect: (%s, %s)" % (self.host, self.port)
                self.sock.connect(sa)
            except socket.error, msg:
                if self.debuglevel > 0:
                    print 'connect fail:', (self.host, self.port)
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue
            break
        if not self.sock:
            raise socket.error, msg

class HTTPTimeout(Exception):
    """
    Exception corresponding to HTTP timeout
    """
    def __str__(self):
        return "HTTP request timed out"

class WbAccessException(Exception):
    """
    Exception corresponding to failure when accessing a WebBrick
    """
    def __init__(self, msg=None, err=0):
        self.msg = msg
        self.err = err

    def __str__(self):
        msg = self.msg or ""
        if self.err: msg += ", wbError="+str(self.err)
        return "WbAccessException: "+msg

# End.
# $Id: WbAccess.py 2612 2008-08-11 20:08:49Z graham.klyne $
    