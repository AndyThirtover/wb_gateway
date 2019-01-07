# Copyright Andy Harris 2019
# Licenced under 3 clause BSD licence 
#
#
#  Solar Control System
#
#  Andy Harris --- 1st January 2019
#
#
#    <eventInterface  module='EventHandlers.UnderFloorHeating' name='UnderFloorHeating' >
#        <zone_temperature type='http://id.webbrick.co.uk/zones/zone' source='zone7/state' />  
#        <run_event type='http://id.webbrick.co.uk/zones/zone' source='zone7/run' />  
#        <stop_event type='http://id.webbrick.co.uk/zones/zone' source='zone7/stop' />  
#        <air_temperature type='http://id.webbrick.co.uk/events/webbrick/CT' source='webbrick/999/CT/0' />  
#        <floor_temperature type='http://id.webbrick.co.uk/events/webbrick/CT' source='webbrick/999/CT/1' />  
#   </eventInterface>

import logging
import time

from EventLib.Event           import Event
from EventLib.Status          import StatusVal
from EventLib.SyncDeferred    import makeDeferred

from EventHandlers.BaseHandler import BaseHandler

from EventHandlers.Utils import *

# make logging global to module.
#_log = None
_log = logging
_log.basicConfig(level=logging.DEBUG, filename='UnderFloorHeating.log')

CONFIG_TYPE = "http://id.webbrick.co.uk/events/config/get"

class UnderFloorHeating( BaseHandler ):
    """
    UnderFloorHeating class that subscribes to events and generates UnderFloorHeating events.
    It's function is to modulate the power of a heating element based on floor temperature and air temperature.
    Floor Temperature should never exceed floor_limit and the system should modulate as air temperature is approached.
    _modulation sets the range over which modulation will occur, below this value 100% power will be supplied.
    """
    
    def __init__ (self, localRouter):
        super(UnderFloorHeating,self).__init__(localRouter)
        global _log
        _log = self._log    # make global

        _log.debug('UnderFloorHeating Initialising')

        self._debug = True  # 
        self._state = None  #  Used for tracking overall state - can be 'stopped','running' and 'over temperature'

        self._underfloor_run_evt_type = 'http://id.webbrick.co.uk/events/UnderFloorHeating'
        self._underfloor_run_evt_source = self._log.name

        self._modulation = 2.0     # the range over which we will modulate
        self._target = 20.0        #  a default target temperature        

        self._floor_event = None
        self._floor_temperature = None
        self._floor_limit = 28 # floor should not go beyond 28 DegC

        self._air_event = None
        self._air_temperature = None

    def start(self):
        self._log.debug( 'start' )
        self._localRouter.subscribe( self._subscribeTime, self, 'http://id.webbrick.co.uk/events/config/get' )
        self._localRouter.subscribe( self._subscribeTime, self, 'http://id.webbrick.co.uk/events/time/minute', 'time/minute' )
        #
        #  Subscribe to the enable and check_time event type
        #
        if self._run_event :
            self._localRouter.subscribe( self._subscribeTime, self, self._run_event['type'] )
        if self._stop_event :
            self._localRouter.subscribe( self._subscribeTime, self, self._stop_event['type'] )
        if self._floor_event :
            self._localRouter.subscribe( self._subscribeTime, self, self._floor_event['type'] )
        if self._air_event :
            self._localRouter.subscribe( self._subscribeTime, self, self._air_event['type'] )

        self.subscribeAll()


    def stop(self):
        self._log.debug( 'stop' )
        if self._debug:
            self._log.debug ("--------- Variables Were ----------------")
            self._log.debug ("MyType %s" % str(self._underfloor_run_evt_type))    
            self._log.debug ("MySource %s" % str(self._underfloor_run_evt_source))    
            self._log.debug ("Floor_Temperature %s" % str(self._floor_temperature))    
            self._log.debug ("Air_Temperature %s" % str(self._air_temperature))    
            self._log.debug ("-----------------------------------------")
        self._localRouter.unsubscribe( self, 'http://id.webbrick.co.uk/events/config/get' )
        self._localRouter.unsubscribe( self, 'http://id.webbrick.co.uk/events/time/minute', 'time/minute' )
        if self._run_event :
            self._localRouter.unsubscribe( self, self._run_event['type'] )
        if self._stop_event :
            self._localRouter.unsubscribe( self, self._stop_event['type'] )

        self.unSubscribeAll()


    def configure( self, cfgDict ):
        from string import upper
        super(UnderFloorHeating,self).configure(cfgDict)

        self._log.debug(cfgDict)

        if cfgDict.has_key('run_event'):
            self._run_event = cfgDict['run_event']
        if cfgDict.has_key('stop_event'):
            self._stop_event = cfgDict['stop_event']
        if cfgDict.has_key('air_temperature'):
            self._air_event = cfgDict['air_temperature']
        if cfgDict.has_key('floor_temperature'):
            self._floor_event = cfgDict['floor_temperature']

        if cfgDict.has_key('eventtype'):
            if cfgDict['eventtype'].has_key('type'):
                self._UnderFloorHeating_evt_type = cfgDict['eventtype']['type']
            
            if cfgDict['eventtype'].has_key('eventsource'):
                if cfgDict['eventtype']['eventsource'].has_key('source'):
                    self._UnderFloorHeating_evt_source = cfgDict['eventtype']['eventsource']['source']
           
        if self._debug:
            self._log.debug ("--------- Config Debug ----------------")
            self._log.debug ("Modulation %s" % str(self._modulation))    
            self._log.debug ("Floor Limit %s" % str(self._floor_limit))    
            self._log.debug ("Run Event %s" % str(self._run_event))
            self._log.debug ("Stop Event %s" % str(self._stop_event))
            self._log.debug ("---------------------------------------")

    def doActions( self, actions, inEvent ):
        if actions:
            for action in actions:
                # logged in BaseHandler.sendEvent
                self._log.debug( 'Generate event %s' % ( action ) )
                self.sendEvent( makeNewEvent( action, inEvent, None ) )
                
    def configureActions( self, cfgDict ):
        self._log.debug("configureActions %s" % (cfgDict) )
        result = None
        if cfgDict.has_key("newEvent"):
            if isinstance( cfgDict["newEvent"], list ):
                result = cfgDict["newEvent"]
            else:
                result = list()
                result.append(cfgDict["newEvent"])
        self._log.debug("configureActions %s" % (result) )
        return result

    def sendUnderFloorHeatingEvent(self, new_output, reason='event'):
        self._log.debug ("Sending UnderFloorHeating Event: %s" % new_output)
        self._UnderFloorHeating_event = Event(self._UnderFloorHeating_evt_type,self._UnderFloorHeating_evt_source, {'output': new_output, 'reason': reason} ) 
        self.sendEvent( self._UnderFloorHeating_event)
        self._UnderFloorHeating_event = None  # reset


    def doHandleConfig( self, inEvent ):
        from string import upper
        src = inEvent.getSource()
        #self._log.debug ("Found Event: %s"  % str(inEvent))
        #self._log.debug ("Handle Config Event SRC %s" % str(src))
        #
        #  Now see if this matches anything we need - which at the moment is nothing, but we could have modulation in the future
        #
        '''if self._check_event['type'] == CONFIG_TYPE:
            if self._check_event['source'] == src:
                self._check_time = int(inEvent.getPayload()['val'])'''


    def bounds(input):
        input = float(input)
        if input > 1.0:
            return 1.0
        if input < 0.0:
            return 0.0
        return input



    def doHandleEvent( self, handler, inEvent ):

        self._log.debug('inEvent handled %s with %s' % (inEvent.getType(), inEvent.getSource()))
    
        if inEvent.getType() == 'http://id.webbrick.co.uk/events/config/get':
            self.doHandleConfig( inEvent )
            return makeDeferred(StatusVal.OK)            

        elif inEvent.getType() == "http://id.webbrick.co.uk/events/time/minute":
            now = int(inEvent.getPayload()['minute'])
            self.Evaluate_Conditions('minute')
            return makeDeferred(StatusVal.OK)
 
        elif self._run_event and inEvent.getType() == self._run_event['type'] and inEvent.getSource() == self._run_event['source']:
            self._state = 'running'
            self.Evaluate_Conditions('run')

        elif self._stop_event and inEvent.getType() == self._stop_event['type'] and inEvent.getSource() == self._stop_event['source']:
            self._state = 'stopped'
            self.Evaluate_Conditions('stop')
 
        elif self._air_event and inEvent.getType() == self._air_event['type'] and inEvent.getSource() == self._air_event['source']:
            self._air_temperature = float(inEvent.getPayload()['val'])
            self._log.debug('Changing Air Temperature to %s' % self._air_temperature)
            self.Evaluate_Conditions('air_temperature')
            return makeDeferred(StatusVal.OK)    

        elif self._floor_event and inEvent.getType() == self._floor_event['type'] and inEvent.getSource() == self._floor_event['source']:
            self._floor_temperature = float(inEvent.getPayload()['val'])
            self._log.debug('Changing Floor Temperature to %s' % self._floor_temperature)
            self.Evaluate_Conditions('floor_temperature')
            return makeDeferred(StatusVal.OK)    

        else: 
            return super(UnderFloorHeating,self).doHandleEvent( handler, inEvent)
            

    def Evaluate_Conditions(self, why):
        #To get here we should running, and have air and floor temperatures available
        self._log.debug('Here we go with evaluation, reason %s, air %s, floor %s' % why, self._air_temperature, self._floor_temperature)
        # Lets do it

        if self._floor_temperature > self._floor_limit:
            self._log.debug('Set floor to stop OVERTEMPERATURE %s' % self._floor_temperature)
            self.sendUnderFloorHeatingEvent(0,'over temperature')
            self._state = 'over_temperature'
            return # nothing more to do

        if self._floor_temperature and self._air_temperature:
            # only evaluate if you have both temperatures available

            if (self._air_temperature < (self._target - self._modulation)):
                # within modulation of floor temperaure
                output = bounds(((self._floor_limit-self._floor_temperature)/self._modulation))
                self.sendUnderFloorHeatingEvent(int(output*100),'floor modulation')
                return 
            elif (self._air_temperature < self._target):
                #within modulation of air temperature
                output = bounds(((self._target-self._air_temperature)/self._modulation))
                self.sendUnderFloorHeatingEvent(int(output*100),'air modulation')
                return 

            if (self._air_temperature > self._target):
                # we are above target, nothing to do.
                self.sendUnderFloorHeatingEvent(0,'air target reached')
                return 


