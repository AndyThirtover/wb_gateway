# Copyright L.P.Klyne 2013 
# Licenced under 3 clause BSD licence 

#
#  Class to handle event actions that are implemented as an email
#
#  Lawrence Klyne
#  Andy Harris -- Modified for SMTP login
#
#
#
import logging

from EventLib.Event import Event
from EventLib.Status          import StatusVal
from EventLib.SyncDeferred    import makeDeferred

from EventHandlers.BaseHandler import BaseHandler

import smtplib
from email.MIMEText import MIMEText

_log = None

#
# WebBrick Email Handler
#
class EmailAction( BaseHandler ):
    """
    Handle events targetting email

    <eventInterface     module='EventHandlers.EmailAction' 
                        name='EmailAction' 
                        smartHost='localhost' 
                        smartPort='20998'
                        username='webbrick'
                        password='password' 
                        from='WebbrickGateway@localhost'>
                        
        <eventtype type="">
            <eventsource source="webbrick/100/DO/0" >
	        <event>
                    <params>
                    </params>
                    <email>
                        <to>TestUser</to>
                        <from>TestUser</from>
                        <body>TestUser %(state)s</body>
                        <subject>TestUser %(state)s</subject>
                    </email>
	        </event>
            </eventsource>
        </eventtype>
    </eventInterface>

    A typical configuration is as above, most is as per BaseHandler with the contents of the email
    element being the details to send a single email. Within this element are elements for 'to address', 'from address'
    the 'body' and the 'subject' The later two may have values substituted in from the initiating event. If the from
    address is not supplied then the default from address specified in the attributes of the eventInterface is used.

    The eventInterface has the following attributes, smartHost the IP/DNS address of the system that handles mail
    routing, smartPort the TCP port number on that host deafults to 25. the 'from' attribute provides a default
    from address for emails that do not have a configured address of their own.

    The value substition is handled by Python standard string formatting using a look up dictionary. 
    For general use this means that a string of the form %(key)s is replaced by looking up key in the 
    event other data attributes.

    See the event specific configuration for keys into the event other data. 
    """

    def __init__ (self, localRouter):
        super(EmailAction,self).__init__(localRouter)
        global _log
        _log = self._log
        self.smartHost = 'localhost'
        self.smartPort = 25

    def configure( self, cfgDict ):
        self.login = False
        if cfgDict.has_key('smartHost'):
            self.smartHost = cfgDict['smartHost']
        if cfgDict.has_key('smartPort'):
            self.smartPort = int(cfgDict['smartPort'])
        if cfgDict.has_key('username'):
            self.username = cfgDict['username']
            self.login = True
        if cfgDict.has_key('password'):
            self.password = cfgDict['password']

        _log.debug( 'SmartHost %s:%s' % (self.smartHost,self.smartPort) )

        if cfgDict.has_key('from'):
            self.From = cfgDict['from']
        super(EmailAction,self).configure( cfgDict )

    def configureActions( self, cfgDict ):
        # The actions are a dictionary of values for the email.
        result = None
        if cfgDict.has_key("email"):
            if isinstance( cfgDict["email"], list ):
                result = cfgDict["email"]
            else:
                result = list()
                result.append(cfgDict["email"])
        return result

    def doActions( self, actions, inEvent ):
        self.connection_status = False
        mailObj = smtplib.SMTP()
        try:
            conn_res = mailObj.connect( self.smartHost, self.smartPort )
            _log.debug( 'SMTP Connect to %s: %s' % (self.smartHost, conn_res[0]) )
            if (conn_res[0] in range(200,300)):
                self.connection_status = True
        except Exception, ex:
            _log.debug( 'SMTP Connection Error to %s' % self.smartHost )
        
        if (self.login and self.connection_status):
            auth_res = mailObj.login(self.username, self.password)
            _log.debug( 'SMTP Login of %s : %s' % (self.username, auth_res[1]) )
            
        od = inEvent.getPayload()
        for action in actions:
            _log.debug( 'doActions %s' % (action) )
            try:
                body = ''
                subject = ''
				#
				#  ToDo substitutions in the TO field
				#
                if action.has_key('body'):
                    body = action['body']['']
                if action.has_key('subject'):
                    subject = action['subject']['']

                if od:
                    if '%' in body:
                        body = body % od
                    if '%' in subject:
                        subject = subject % od

                msg = MIMEText(body)

                msg['Subject'] = subject

                if action.has_key('from'):
                    msg['From'] = action['from']['']
                else:
                    msg['From'] = self.From
				#
				# ToDo  Handle multiple RCPTS  (RFC821)
				#
                msg['To'] = action['to']['']

                mailObj.sendmail(msg['From'], msg['To'], msg.as_string())

            except Exception, ex:
                _log.exception( "SMTP Exception from %s: %s" % (self.smartHost, ex) )
