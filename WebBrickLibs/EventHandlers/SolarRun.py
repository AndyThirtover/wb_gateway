# Copyright Andy Harris 2016 
# Licenced under 3 clause BSD licence 

#
#
#  Solar Control System
#
#  Andy Harris --- 30th January 2016
#
#
#    <eventInterface  module='EventHandlers.SolarRun' name='SolarRun' >
#        <check_time type='http://id.webbrick.co.uk/events/config/get' source='solar_check_time' />   
#        <check_run_time type='http://id.webbrick.co.uk/events/config/get' source='solar_check_run_time' />   
#        <enable type='http://id.webbrick.co.uk/events/config/get' source='solar_enable' />  
#        <pump type='http://id.webbrick.co.uk/events/webbrick/DO' source='webbrick/36/DO/4' key="state" invert="true" />  
#        <pipe_temperature type='http://id.webbrick.co.uk/events/webbrick/CT' source='webbrick/999/CT/0' />  
#        <tank_temperature type='http://id.webbrick.co.uk/events/webbrick/CT' source='webbrick/999/CT/1' />  
#        
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
_log.basicConfig(level=logging.DEBUG, filename='/var/log/webbrick/SolarRun.log')

CONFIG_TYPE = "http://id.webbrick.co.uk/events/config/get"

class SolarRun( BaseHandler ):
    """
    SolarRun class that subscribes to events and generates SolarRun events
    """
    
    def __init__ (self, localRouter):
        super(SolarRun,self).__init__(localRouter)
        global _log
        _log = self._log    # make global

        _log.debug('SolarRun Initialising')

        self._debug = True  # 
        self._counter = 0   #  Will be used for counting
        self._state = None  #  Used for tracking overall state

        self._solar_run_evt_type = 'http://id.webbrick.co.uk/events/SolarRun'
        self._solar_run_evt_source = self._log.name

        self._check_time = 120
        self._check_event = None
        self._enable = False
        self._enable_event = None

        self._threshold = 6.0     # default to 6 degrees of difference between pipe and tank
        
        self._isDark = 0           # a default value
        self._dayphasetext = "Unknown"  # a default value

        self._pump_state = None
        self._pump_event = None
        self._pump_check_run = False
        self._pump_check_start = None

        self._pump_check_run_time_event = None
        self._pump_check_run_time = 1  # pump will run for 60 seconds before we decide that we have heat in the pipes.

        self._tank_event = None
        self._tank_temperature = None
        self._tank_limit = 80 # tank should not go beyond 80 DegC

        self._pipe_event = None
        self._pipe_temperature = None

    def start(self):
        self._log.debug( 'start' )
        self._localRouter.subscribe( self._subscribeTime, self, 'http://id.webbrick.co.uk/events/config/get' )
        self._localRouter.subscribe( self._subscribeTime, self, 'http://id.webbrick.co.uk/events/time/dayphaseext' )
        self._localRouter.subscribe( self._subscribeTime, self, 'http://id.webbrick.co.uk/events/time/isDark' )
        self._localRouter.subscribe( self._subscribeTime, self, 'http://id.webbrick.co.uk/events/time/second', 'time/second' )
        self._localRouter.subscribe( self._subscribeTime, self, 'http://id.webbrick.co.uk/events/time/minute', 'time/minute' )
        #
        #  Subscribe to the enable and check_time event type
        #

        if self._enable_event :
            self._localRouter.subscribe( self._subscribeTime, self, self._enable_event['type'] )
        if self._check_event :
            self._localRouter.subscribe( self._subscribeTime, self, self._check_event['type'] )
        if self._pump_event :
            self._localRouter.subscribe( self._subscribeTime, self, self._pump_event['type'] )
        if self._pump_check_run_time_event :
            self._localRouter.subscribe( self._subscribeTime, self, self._pump_check_run_time_event['type'] )
        if self._tank_event :
            self._localRouter.subscribe( self._subscribeTime, self, self._tank_event['type'] )
        if self._pipe_event :
            self._localRouter.subscribe( self._subscribeTime, self, self._pipe_event['type'] )

        self.subscribeAll()


    def stop(self):
        self._log.debug( 'stop' )
        if self._debug:
            self._log.debug ("--------- Variables Were ----------------")
            self._log.debug ("MyType %s" % str(self._solar_run_evt_type))    
            self._log.debug ("MySource %s" % str(self._solar_run_evt_source))    
            self._log.debug ("Enabled %s" % str(self._enable))    
            self._log.debug ("Check Time %s" % str(self._check_time))    
            self._log.debug ("DayPhase %s" % str(self._dayphasetext))    
            self._log.debug ("Dark %s" % str(self._isDark))    
            self._log.debug ("PumpState %s" % str(self._pump_state))    
            self._log.debug ("Tank_Temperature %s" % str(self._tank_temperature))    
            self._log.debug ("-----------------------------------------")
        self._localRouter.unsubscribe( self, 'http://id.webbrick.co.uk/events/config/get' )
        self._localRouter.unsubscribe( self, 'http://id.webbrick.co.uk/events/time/dayphaseext' )
        self._localRouter.unsubscribe( self, 'http://id.webbrick.co.uk/events/time/isDark' )
        self._localRouter.unsubscribe( self, 'http://id.webbrick.co.uk/events/time/second', 'time/second' )
        self._localRouter.unsubscribe( self, 'http://id.webbrick.co.uk/events/time/minute', 'time/minute' )
        if self._enable_event :
            self._localRouter.unsubscribe( self, self._enable_event['type'] )
        if self._check_event :
            self._localRouter.unsubscribe( self, self._check_event['type'] )

        self.unSubscribeAll()


    def configure( self, cfgDict ):
        from string import upper
        super(SolarRun,self).configure(cfgDict)

        self._log.debug(cfgDict)

        if cfgDict.has_key('enable'):
            self._enable_event = cfgDict['enable']
        if cfgDict.has_key('check_time'):
            self._check_event = cfgDict['check_time']
        if cfgDict.has_key('pump'):
            self._pump_event = cfgDict['pump']
        if cfgDict.has_key('check_run_time'):
            self._pump_check_run_time_event = cfgDict['check_run_time']
        if cfgDict.has_key('pipe_temperature'):
            self._pipe_event = cfgDict['pipe_temperature']
        if cfgDict.has_key('tank_temperature'):
            self._tank_event = cfgDict['tank_temperature']

        if cfgDict.has_key('eventtype'):
            if cfgDict['eventtype'].has_key('type'):
                self._SolarRun_evt_type = cfgDict['eventtype']['type']
            
            if cfgDict['eventtype'].has_key('eventsource'):
                if cfgDict['eventtype']['eventsource'].has_key('source'):
                    self._SolarRun_evt_source = cfgDict['eventtype']['eventsource']['source']
           
        if self._debug:
            self._log.debug ("--------- Config Debug ----------------")
            self._log.debug ("Check Time %s" % str(self._check_time))    
            self._log.debug ("Check Run Time %s" % str(self._pump_check_run_time))    
            self._log.debug ("enable event %s" % str(self._enable_event))
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


    def indexSolarRun(self, inEvent):
        self._log.debug('checking if there is anything to do at this time')
        if self._pump_check_run:
            self.Evaluate_Conditions('tick')

    def setSolarRunEvent(self):
        self._log.debug ("Setting SolarRun Event ....")
        self._SolarRun_event = Event(self._SolarRun_evt_type,self._SolarRun_evt_source, {'hold': self._hold, 'occupancy': self._occupancy, 'isDark': self._isDark, 'dayphase': self._dayphasetext, 'presence': self._presence, 'light_state': self._light_state} ) 
        self._counter = 0         # reset


    def sendSolarRunEvent(self, new_pump_state):
        self._log.debug ("Sending SolarRun Event: %s" % new_pump_state)
        self._SolarRun_event = Event(self._SolarRun_evt_type,self._SolarRun_evt_source, {'set_pump_state': new_pump_state,
                                                                                        'pump_state': self._pump_state} ) 
        self.sendEvent( self._SolarRun_event)
        self._SolarRun_event = None  # reset


    def doHandleConfig( self, inEvent ):
        from string import upper
        src = inEvent.getSource()
        #self._log.debug ("Found Event: %s"  % str(inEvent))
        #self._log.debug ("Handle Config Event SRC %s" % str(src))
        #
        #  Now see if this matches anything we need
        #
        if self._enable_event:
            if self._enable_event['type'] == CONFIG_TYPE:
                if self._enable_event['source'] == src:
                    en = inEvent.getPayload()['val']
                    if en == "1":
                        self._enable = True
                    if upper(en) == "TRUE":
                        self._enable = True
                    else:
                        self._enable = False

        if self._check_event['type'] == CONFIG_TYPE:
            if self._check_event['source'] == src:
                self._check_time = int(inEvent.getPayload()['val'])

        if self._pump_check_run_time_event['type'] == CONFIG_TYPE:
            if self._pump_check_run_time_event['source'] == src:
                self._pump_check_run_time = int(inEvent.getPayload()['val'])
                    

    def doHandleDayPhase( self, inEvent ):
        src = inEvent.getSource()
        #self._log.debug ("Found Event: %s"  % str(inEvent))
        #self._log.debug ("Handle DayPhase Event SRC %s" % str(src))
        if src == 'time/dayphaseext':
            self._dayphasetext = inEvent.getPayload()['dayphasetext']


    def doHandleDark( self, inEvent ):
        src = inEvent.getSource()
        #self._log.debug ("Found Event: %s"  % str(inEvent))
        #self._log.debug ("Handle Dark Event SRC %s" % str(src))
        if src == 'time/isDark':
            self._isDark = inEvent.getPayload()['state']


    def doHandleEvent( self, handler, inEvent ):

        self._log.debug('inEvent handled %s with %s' % (inEvent.getType(), inEvent.getSource()))
    
        if inEvent.getType() == 'http://id.webbrick.co.uk/events/config/get':
            self.doHandleConfig( inEvent )
            return makeDeferred(StatusVal.OK)    
        
        elif inEvent.getType() == 'http://id.webbrick.co.uk/events/time/dayphaseext':
            self.doHandleDayPhase( inEvent ) 
            return makeDeferred(StatusVal.OK)   
        
        elif inEvent.getType() == 'http://id.webbrick.co.uk/events/time/isDark':
            self.doHandleDark( inEvent )
            self.Evaluate_Conditions('DayNightChange')
            return makeDeferred(StatusVal.OK)    
        
        elif inEvent.getType() == "http://id.webbrick.co.uk/events/time/second":
            self.indexSolarRun(inEvent)
            return makeDeferred(StatusVal.OK)

        elif inEvent.getType() == "http://id.webbrick.co.uk/events/time/minute":
            now = int(inEvent.getPayload()['minute'])
            if (now%self._check_time == 0) and self._enable and not self._isDark:
                self.Evaluate_Conditions('check')
            return makeDeferred(StatusVal.OK)
        
        elif self._pump_event and inEvent.getType() == self._pump_event['type'] and inEvent.getSource() == self._pump_event['source']:
            self._pump_state = int(inEvent.getPayload()['state'])
            self._log.debug('Changing Pump State to %s' % self._pump_state)
            return makeDeferred(StatusVal.OK)    

        elif self._pipe_event and inEvent.getType() == self._pipe_event['type'] and inEvent.getSource() == self._pipe_event['source']:
            self._pipe_temperature = float(inEvent.getPayload()['val'])
            self._log.debug('Changing Pipe Temperature to %s' % self._pipe_temperature)
            self.Evaluate_Conditions('pipe_temperature')
            return makeDeferred(StatusVal.OK)    

        elif self._tank_event and inEvent.getType() == self._tank_event['type'] and inEvent.getSource() == self._tank_event['source']:
            self._tank_temperature = float(inEvent.getPayload()['val'])
            self._log.debug('Changing Tank Temperature to %s' % self._tank_temperature)
            self.Evaluate_Conditions('tank_temperature')
            return makeDeferred(StatusVal.OK)    



        else: 
            return super(SolarRun,self).doHandleEvent( handler, inEvent)
            

    def Evaluate_Conditions(self, why):
        #To get here we should be enabled, it should light and we are either at an evaluation time, or we have been running
        self._log.debug('Here we go with evaluation, reason %s' % why)
        self._log.debug('Tank_Temperature : %s' % self._tank_temperature)
        self._log.debug('Pipe_Temperature : %s' % self._pipe_temperature)
        self._log.debug('pump_state : %s' % self._pump_state)
        self._log.debug('State : %s' % self._state)
        self._log.debug('pump_check_run : %s' % self._pump_check_run)
        self._log.debug('pump_check_run_time : %s' % self._pump_check_run_time)
        # Lets do it

        if self._tank_temperature > self._tank_limit:
            self._log.debug('Set pump to stop OVERTEMPERATURE %s' % self._tank_temperature)
            self.sendSolarRunEvent('stop')
            self._state = 'over_temperature'

        if why == 'check':
            if (self._pump_state == 0) and (self._pump_check_run == False):
                self._log.debug('Set pump to checking')
                self.sendSolarRunEvent('check_run')
                self._pump_check_run = True
                self._state = 'checking'
                self._pump_check_start = time.time()


        if self._tank_temperature and self._pipe_temperature:
            # only evaluate if you have both temperatures available
            if (self._pipe_temperature + self._threshold) > self._tank_temperature:
                # pipe is hot pump should run as long as the tank is not over temperature
                if self._tank_temperature < self._tank_limit:
                    self._log.debug('Set pump to run %s - %s' % (self._pipe_temperature, self._tank_temperature))
                    self.sendSolarRunEvent('run')
                    self._state = 'run'

            if (self._pipe_temperature + self._threshold) < self._tank_temperature:
                if self._pump_check_run:
                    if (time.time() - self._pump_check_start) < self._pump_check_run_time:
                        # Do nothing until the check run is complete
                        self._log.debug('Waiting for check_run to complete')
                        pass
                else:
                    # Pump check run as come to an end
                    self._log.debug('Set pump to stop, not in checking, low differential %s - %s' % (self._pipe_temperature, self._tank_temperature))
                    self._pump_check_run = False
                    self.sendSolarRunEvent('stop')
                    self._state = 'idle'


        if self._isDark:
            # its dark stop the pump
            self._log.debug('Set pump to stop because dark')
            self.sendSolarRunEvent('stop')
            self._state = 'inDarkness'




