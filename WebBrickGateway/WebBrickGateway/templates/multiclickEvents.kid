<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python
from turbogears import config as tgconfig
import re
serverHost = "127.0.0.1:%s"%(tgconfig.get("server.socket_port", "8080", False, "global" ))
zoneLimit = 0

def getCurrentValue( uri ):
    """
    attempt to retrieve the current value of the uri passed
    """
    try:
        from WebBrickLibs.WbAccess import GetHTTPXmlDom
        from MiscLib.DomHelpers import getNamedNodeText
        dom = GetHTTPXmlDom( serverHost, uri )    # need to know self address
        if dom:
            return getNamedNodeText(dom, 'val')
    except:
        from logging import getLogger
        getLogger( "WebBrickGateway.templates.widgets" ).exception( "getCurrentValue %s " % (uri) )
    return '' 

    
def zoneEvLog(searchSpec, searchSpec2='.'):
    payload=""
    fname = "/var/log/webbrick/EventLog.log"
    inFn = file(fname)
    for line in inFn:
        if re.search(searchSpec,line):
            if re.search(searchSpec2,line):
                payload = payload + "<br/>" + line
    return payload

?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" xmlns:ui="ui" >
	  
<head>
	<link href="/static/css/diag.css" type="text/css" rel="stylesheet" />
 </head>
<body>

<a href='#' onClick="window.location.reload()">Reload</a>
<a href='/template/diag'>Diagnostics Home</a>
<a href='/'>Interface Home</a>
    
<h1>MultiClick events</h1>

<p>These events are taken from the current event log, any digital trigger with more than one click is shown</p>


<h2>Multiclicks</h2>

    ${XML(zoneEvLog("'val': [2-9],","/TD/"))} 

<h2>All Digital Triggers</h2>

    ${XML(zoneEvLog("/TD/"))}


</body>
</html>