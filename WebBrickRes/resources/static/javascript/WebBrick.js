// $Id: WebBrick.js 3715 2010-09-10 10:14:40Z tombushby $
//
// Javascript library to support WebBrick control panel interaction widgets

// These are part of the polling, defined here as global.
pollerEvent    = null;
pollerDeferred = null ;

// these are specified here so can be modified on a per platform/page basis.
var pollerInterval = 6.5;
var pollerTimeout = 15.0;
var pollerSoonDelay = 1.0;

// ----------------------------------------------------------------
// General functions
// ----------------------------------------------------------------

// Apply a supplied function to every named element in a DOM tree or subtree
// vals, if supplied, is a list of values that are supplied to function calls
// for the the dom elements walked.
function domWalk(domref,func,elemname,vals)
    {
    logDebug( "domWalk: ", domref, ", ", elemname, ", ", vals) ;
    if (elemname == null ) elemname = "*"
    var elems = domref.getElementsByTagName(elemname) ;
    for (var i = 0 ; i < elems.length ; i++)
        {
        if ( vals )
            {
            func(elems[i],i,vals) ;
            }
        else
            {
            func(elems[i],i) ;
            }
        
        }
    }

// Find the first child element of a node (i.e. skip any text nodes)
function getFirstChildElem(elem)
    {
    logDebug("getFirstChildElem: ", elem.nodeName, ", len: ", elem.childNodes.length) ;
    for ( var i = 0 ; i < elem.childNodes.length ; i++ )
        {
        var n = elem.childNodes[i] ;
        if (n.nodeType == 1) return n ;
        }
    return null ;
    }

// Extract all child text from DOM element node
function getElementText(elem)
    {
    if ( elem == null ) return "" ;
    logDebug("getElementText: ", elem.childNodes) ;
    var txt = "" ;
    for ( var i = 0 ; i < elem.childNodes.length ; i++ )
        {
        if ( elem.childNodes[i].nodeType == 3 )
            {
            txt += elem.childNodes[i].nodeValue ;
            }
        }
    return txt ;
    }

// Extract the text from the first child node with the given name
function getElementTextByTagName(elem, elemname)
    {
    var txt = "" ;
    var nodes = elem.getElementsByTagName(elemname);
    if ( nodes.length > 0 )
        {
        txt = getElementText(nodes[0]);
        }
    return txt ;
    }

// Extract the text from the first child node with the given name
// The attempt to convert to numeric value
function getElementIntByTagName(elem, elemname)
    {
    var txt = getElementTextByTagName(elem, elemname);
    if ( txt != null )
        {
        var pat = /^\d+$/ ;         // digit digit*
        if ( pat.test(txt) )
            {
            return parseInt(txt);
            }
        }
    return null ;
    }

// Extract the text from the first child node with the given name
// The attempt to convert to numeric value
function getElementFloatByTagName(elem, elemname)
    {
    var txt = getElementTextByTagName(elem, elemname);
    if ( txt != null )
        {
        var pat = /^(\+|-)?\d+(.\d*)?$/ ;  // [+|-]digit digit* [ "." digit* ]
        if ( pat.test(txt) )
            {
            return parseFloat(txt);
            }
        }
    return null ;
    }

// Set text value in DOM element node:  
// Replaces all children of the node with just one containing the supplied text.
function setElementText(elem, text)
    {
    logDebug("setElementText: ", elem, ", ", text) ;
    replaceChildNodes(elem, text);
    return elem ;
    }


// ----------------------------------------------------------------
// Initialise widget callbacks
// ----------------------------------------------------------------

// Scan all DOM elements for wbLoad attributes, and call the indicated 
// function for each such element, supplying the element object as an
// argument.  This allows each element to perform its own onload 
// initialization, independently of all the other elements on a panel.
//
// This function should be activated as an 'onLoad' attribute on the 
// HTML page <body> element.
//
function InitPanelElements(window)
    {
    logDebug( "InitPanelElements: ", window ) ;
    reload = subscribe( "PollerEvent", checkReload ) ;
    try
        {
        // initPoller( 30.0 ) ;    // Init poller with 30 second interval
        domWalk(document,InitPanelElement) ;
        // pollNow() ;             // Start poller now
        }
    catch( e )
        {
        logError("InitPanelElements: ", e) ;
        }
    }

function InitPanelElement(elm)
    {
    logDebug( "InitPanelElement: ", elm.tagName );
    var fname = elm.getAttribute("wbLoad") ;
    if ( fname )
        {
        }
    else
        {
        fname = elm.getAttribute("wbType") ;
        logDebug( "InitPanelElement: ", fname, ", ", elm );
        if ( fname )
            {
            fname = "load"+fname+"()";
            }
        }
    if ( fname )
        {
        // Assume that 'eval' content executes in current function context
        // hence 'elm' accesses the argument to this function.
        // alert("InitPanelElement: "+fname) ;
        logDebug( "InitPanelElement (eval): ", fname, ", ", elm );
        try
            {
            eval( fname+"(elm)" ) ;
            }
        catch( e )
            {
            logError("InitPanelElement: ", e) ;
            }
        }
 // MCFocusable= "true"        
    var fname = elm.getAttribute("wbTarget");
    if ( fname )
        {
        elm.setAttribute( "MCFocusable", "true")
        }
    fname = elm.getAttribute("onClick")
    if ( fname )
        {
        elm.setAttribute( "MCFocusable", "true")
        }

    // a workaround for IE issues
    if ( elm.tagName == "BUTTON" )
        {
        connect(elm, 'onclick', buttonClick(elm) );
        }
    }

function buttonClick(elm)
    {
    return function()
        {
        buttonClickCB(elm);
        } 
    }
    
function buttonClickCB(elm)
    {
    // locate hidden input element buttonAction
    // if not found create as child of parent?
    // set value
    buttonAction = currentDocument().getElementById("buttonAction") ;
    if (buttonAction)
        {
        setNodeAttribute(buttonAction, "value", elm.id );
        }
    }

// ------------------------------------------------
// Framework for refreshing displayed values
// ------------------------------------------------

// This framework uses the simple publish-subscribe event framework to periodically
// request a new value to be displayed.  Further, it allows an explicit request
// to be used to immediately refresh the displayed value, rather than waiting for 
// the next polling interval to come around.
//
// To use this framework:
// (a) call initPoller once when a panel is first initialized
// (b) when all initialization code is complete, call pollNow to start the poller.
// (c) for each item whose display requires periodic updating, create an event
//     handler for performing the update.  The event handler should require no
//     additional parameters.
// (d) in the item's initialization phase, call the setPoller function to
//     establish that the refresh function will be called periodically, or
//     more frequently if other events so dictate.
// (e) [optional] when the item is no longer required to be updated, call
//     cancellPoller to stop the periodic updates.  Normally, this would be
//     when the panel is being removed, so should be unnecessary.

function initPoller(interval)
    {
    pollerEvent    = new Event( "PollerEvent", this, { interval: interval } ) ;
    pollerDeferred = null ;
    }

// This function is used to initiate a test for changes soon.
// it's supplied argument is returned for the next callback in the chain.
// The supplied request object is also used as the event source value.
function pollSoon(req)
    {
    logDebug("pollSoon") ;
    try
        { 
        if (pollerDeferred != null)
            {
            pollerDeferred.cancel() ;
            pollerDeferred = null ;
            }
        // Start new timer
        pollerDeferred = callLater( pollerSoonDelay, pollNow );
        }
    catch(e)
        {
        logDebug("pollSoon: ", e);
        }
    }

// This function is intended to be used as a deferred callback function:
// it's supplied argument is returned for the next callback in the chain.
// The supplied request object is also used as the event source value.
function pollNow(req)
    {
    logDebug("pollNow: event:", pollerEvent, ", req: ", req) ;
    // Cancel any outstanding timer, ignore any errors
    try
        { 
        if (pollerDeferred != null)
            {
            pollerDeferred.cancel() ;
            pollerDeferred = null ;
            }
        }
    catch(e)
        {
        logDebug("Cancelled timer: ", e) ;
        }
    // Start new timer
    pollerDeferred = callLater(pollerEvent.interval, pollNow) ;
    // Invoke any listeners
    trigger(pollerEvent, req);
    // Note: new timer is started before event is triggered, so that further immediate
    // pollNow calls from the event trigger don't leave multiple timers outstanding.
    return req ;    // Return request to next in callback chain
    }

function setPoller(func)
    {
    logDebug("setPoller") ;
    if (arguments.length > 1)
        {
        // Partial application of func to remaining arguments:
        func = MochiKit.Base.partial.apply(null, arguments) ;
        }
    handle = subscribe("PollerEvent", partial(callPoller, func)) ;
    
    // test to see whether poller initialised.
    if ( pollerEvent == null)
    {
        initPoller( pollerInterval );
    }
    pollSoon();             // read values sometime in the near future, may be reset if more fields using updates.
    return handle;
    }

function callPoller(func, handle, event, source)
    {
    logDebug("callPoller") ;
    func() ;
    }

function cancelPoller(handle)
    {
    logDebug("cancelPoller") ;
    unsubscribe(handle, "PollerEvent") ;
    }


// ------------------------------------------------
// Simple publish-subscribe framework for events
// ------------------------------------------------

// Event propagation allows any number of event targets to subscribe to be notified
// when any component triggers an event of a specified type.
//
// The basic operations provided are:
//   handle = subscribe(eventType, target) ;
//   unsubscribe(handle, eventType) ;
//   trigger(event, source) ;
//
// 'target' is a function that is called when an event is triggered, with three arguments:
//   - the event subscription handle for which the target is being activated
//   - an instance of the event type
//   - the source that triggered this event
//
// 'handle' is an opaque value, used to cancel a particular subscription.
//
// 'source' is a string that can be used to locate or identify the event source.
// In principle, 'source' is a URI, but this framework does nothing to enforce that.
//
// An event has a type, a source and some other unspecified values based on its type.
//

EventSubscriberList = [] ;        // An array of event subscriptions

function subscribe(eventType, target)
    {
    logDebug("subscribe: ", eventType) ;
    h = getNewHandle(EventSubscriberList) ;
    enrollSubscription(EventSubscriberList, h, eventType, target) ;
    return h ;
    }

function unsubscribe(handle, eventType)
    {
    logDebug("unsubscribe: ", handle, ", ", eventType) ;
    cancelSubscription(EventSubscriberList, handle, eventType) ;
    }

function trigger(event, source)
    {
    //// logDebug("trigger: ", event) ;
    publishEvent(EventSubscriberList, event, source)
    }


// Internal publish-subscribe helper functions
function getNewHandle(sublist)
    {
    for ( var i = 0 ; i < sublist.length ; i++ )
        {
        if ( sublist[i] == null ) return i ;
        }
    return sublist.length ;
    }

function enrollSubscription(sublist, handle, eventType, target)
    {
    logDebug("enrollSubscription: ", eventType) ;
    sublist[handle] = {eventType:eventType, target:target} ;
    }

function cancelSubscription(sublist, handle, eventType)
    {
    logDebug("cancelSubscription: ", eventType) ;
    if ( sublist[handle].eventType == eventType )
        {
        sublist[handle] = null ;
        }
    else
        {
        throw new EventError( this, "cancelSubscription event type mismatch" ) ;
        }
    }

function publishEvent(sublist, event, source)
    {
    //// logDebug("publishEvent: ", event.eventType) ;
    for ( var h = 0 ; h < sublist.length ; h++ )
        {
        if ( sublist[h].eventType == event.eventType )
            {
            sublist[h].target(h, event, source) ;
            }
        }
    }

// Construct a new event
// Specifies a type value, a source value and an object with additional values
// that are added to the event object.
function Event(type, source, obj)
    {
    this.eventType   = type ;
    this.eventSource = source ;
    for (var key in obj)
        {
        this[key] = obj[key] ;
        }
    return this ;
    }

// TODO: figure out how to create a hierarchy of event values.  
// Javascript prototype-based inheritance is pretty confusing.

// Define EventError constructor/class...
// This is an event object with a message value
// TODO: refine as we better understand Javascript classes.
function EventError( source, msg )
    {
    return Event( "EventError", source, { message : msg } ) ;
    }

// ----------------------------------------------------------------
// Support for WebBrick queries via Gateway
// ----------------------------------------------------------------

// Return endpoint locator URI, or null
// Helper function for getEndPointSource and getEndPointTarget
// p1 = uri path before adress
// p2 = uri path after address, before channel
// p3 = uri path after channel
//
function getEndPoint(elem,attrname,p1,p2,p3)
    {
    var attr = elem.getAttribute(attrname) ;
    var path = null ;
    if ( attr )
        {
        var i = attr.lastIndexOf("/") ;
        if ( i >= 0 )
            {
            var addr  = attr.slice(0,i) ;
            var chan  = attr.slice(i+1) ;
            path = p1+addr+p2+chan+p3
            }
        }
    return path ;
    }

// Return an source endpoint locator value (Gateway query path), or null
function getEndPointSource(elem)
    {
    return elem.getAttribute( "wbSource" );
    }

// Return an target endpoint command URI, or null
// (value for sending to target must be appended)
function getEndPointTarget(elem)
    {
    return elem.getAttribute( "wbTarget" );
    }

// Function behaves a bit like 'doSimpleXMLHttpRequest', except that it 
// takes a timeout (seconds) argument and completes the request with a 
// CancelledError condition if the HTTP operation does not complete 
// within the specified time interval
function doTimedXMLHttpRequest(uripath, timeout)
    {
    logDebug("doTimedXMLHttpRequest: ", uripath, ", timeout: ", timeout) ;
    return addTimeout(doSimpleXMLHttpRequest(uripath), timeout) ;
    }

// Accepts a deferred value, and returns a deferred that behaves
// just like the original except that it is cancelled if it fails
// to complete in the specified number of seconds.
function addTimeout(deferred, timeout)
    {
    logDebug("addTimeout: ", timeout) ;
    // Define local canceller function, bound to deferred
    var canceller = callLater(timeout,
        function ()
            {
            // Cancel the deferred after timeout seconds
            logDebug("** Timeout") ;
            deferred.cancel() ;
            } ) ;
    deferred.addBoth(
        function (res) 
            {
            // If the deferred fires, cancel the timeout
            logDebug("** Cancel timeout") ;
            canceller.cancel() ;
            return res;
            } ) ;
    return deferred
    }


// Function to extract status value as string from asynchronously
// completed HTTP request.  
// Returns a triple of address, channel and value string.
//
// Response template:
// <wbStatus wbAddr="${wbAddr}" wbChan="${wbChan}">${stsval}</wbStatus>
//
function getWbStatus(req)
    {
    logDebug("getWbStatus: ", req) ;
    var response = null ;    
    try
        {
        response = req.responseXML.documentElement ;
        }
    catch(e)
        {
        logWarning( "getWbStatus: no WebBrick status: ", e) ;
        }
    if ( response != null )
        {
        var sts = [null,null,null] ;
        sts[0] = response.getAttribute("wbAddr") ;
        logDebug("getWbStatus: sts[0]: ", sts[0]) ;
        sts[1] = response.getAttribute("wbChan") ;
        logDebug("getWbStatus: sts[1]: ", sts[1]) ;
        var n  = getFirstChildElem(response)
        sts[2] = getElementText(n) ;
        logDebug("getWbStatus: n: ", n, ", sts[2]: ", sts[2]) ;
        if ( n != null )
            {
            // allow any element name other than err
            if (n.nodeName != "err")
//            if (n.nodeName == "val")
                {           
                logDebug("getWbStatus: addr", sts[0], ", chan: ", sts[1], ", val: ", sts[2]) ;
                return sts ;
                }
            logDebug("getWbStatus: addr", sts[0], ", chan: ", sts[1], ", err: ", sts[2]) ;
            }
        }
    logDebug("getWbStatus (null return)") ;
    return null ;
    }

// Function to extract status value as integer from asynchronously
// completed HTTP request.  
// Returns a triple of address, channel and value.
function getWbStatusUnsignedInt(req)
    {
    logDebug("getWbStatusUnsignedInt: ", req) ;
    var sts = getWbStatus(req) ;
    if ( sts != null )
        {
        var pat = /^\d+$/ ;         // digit digit*, sign optional
        if ( pat.test(sts[2]) )
            {
            sts[2] = sts[2] - 0 ;   // Force to numeric
            return sts ;
            }
        }
    return null ;
    }

// Function to extract status value as integer from asynchronously
// completed HTTP request.  
// Returns a triple of address, channel and value.
function getWbStatusInt(req)
    {
    logDebug("getWbStatusInt: ", req) ;
    var sts = getWbStatus(req) ;
    if ( sts != null )
        {
        var pat = /^(\+|-)?\d+$/ ;         // digit digit*, sign optional
        if ( pat.test(sts[2]) )
            {
            sts[2] = sts[2] - 0 ;   // Force to numeric
            return sts ;
            }
        }
    return null ;
    }

// Function to extract status value as a real number from 
// an asynchronously completed HTTP request.  
// Returns a triple of address, channel and value.
function getWbStatusUnsignedReal(req)
    {
    logDebug("getWbStatusUnsignedReal: ", req) ;
    var sts = getWbStatus(req) ;
    if ( sts != null )
        {
        var pat = /^\d+(.\d*)?$/ ;  // [+|-]digit digit* [ "." digit* ]
        if ( pat.test(sts[2]) )
            {
            sts[2] = sts[2] - 0 ;   // Force to numeric
            return sts ;
            }
        }
    return null ;
    }

// Function to extract status value as a real number from 
// an asynchronously completed HTTP request.  
// Returns a triple of address, channel and value.
function getWbStatusReal(req)
    {
    logDebug("getWbStatusReal: ", req) ;
    var sts = getWbStatus(req) ;
    if ( sts != null )
        {
        var pat = /^(\+|-)?\d+(.\d*)?$/ ;  // [+|-]digit digit* [ "." digit* ]
        if ( pat.test(sts[2]) )
            {
            sts[2] = sts[2] - 0 ;   // Force to numeric
            return sts ;
            }
        }
    return null ;
    }

// Function to extract Boolean status value as integer from asynchronously
// completed HTTP request.  
// Returns a triple of address, channel and value.
// For False, return 0, for True, return 1.
function getWbStatusBool(req)
    {
    logDebug("getWbStatusBool: ", req) ;
    var sts = getWbStatus(req) ;
    if ( sts != null )
        {
        switch (sts[2])
            {
            case "False":   sts[2] = 0 ;    break ;
            case "True":    sts[2] = 1 ;    break ;
            default:        return null ;
            }
        return sts ;
        }
    return null ;
    }

// Function to extract possible Boolean status value as integer from asynchronously
// completed HTTP request.  
// Returns a triple of address, channel and value.
// For False, return 0, for True, return 1.
function getWbStatusBoolInteger(req)
    {
    logDebug("getWbStatusBool: ", req) ;
    var sts = getWbStatus(req) ;
    if ( sts != null )
        {
        // TODO convert to lower?
        switch (sts[2])
            {
            case "Off":
            case "False":   sts[2] = 0 ;    break ;
            case "On":
            case "True":    sts[2] = 1 ;    break ;
            default:
                var pat = /^\d+$/ ;         // digit digit*
                if ( pat.test(sts[2]) )
                    {
                    sts[2] = sts[2] - 0 ;   // Force to numeric
                    }
                else
                    {
                    sts = null;
                    }
            }
        }
    return sts ;
    }

function getWidgetBaseClass(elm,baseClassName)
{
    elm.baseClassName  = elm.getAttribute("baseClassName");
    if (!elm.baseClassName)
    {
        elm.baseClassName = baseClassName;
    }
}

function setWidgetState(elm,state)
    {
    elm.state     = state ;
    elm.className = elm.baseClassName+state;
    }

// measured in poll intervals.
reloadTimer = 60;   // 10 minutes
function checkReload()
{
    logDebug( "checkReload: ", reloadTimer );
    --reloadTimer;
    if ( reloadTimer == 0 )
    {
        window.location.reload();
//        window.location.href = "/";
//        window.location.href = window.location.host + "/";
    }
}

// Hack as default is no limit and default firebug off
MochiKit.Logging.logger.useNativeConsole = false;
MochiKit.Logging.logger.maxSize = 2000;

// This will get things going.
connect(window, "onload", InitPanelElements ); 

// function to look inside an element
function childNodeById(currentElement, sID)
{
  if (currentElement)
  {
    var result = null;
    if (currentElement.id == sID)
    {
      result = currentElement;
    }
    else
    {
        // Traverse the tree
        var i=0;
        var currentElementChild=currentElement.childNodes[i];
        while (currentElementChild)
        {
          // Recursively traverse the tree structure of the child node
          result = childNodeById(currentElementChild, sID);
          if (result) break;
          i++;
          currentElementChild=currentElement.childNodes[i];
        }
    }
    return result;
  }
}

