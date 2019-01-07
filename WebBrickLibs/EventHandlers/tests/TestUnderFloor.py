# Copyright Andy Harris 2016
# Licenced under 3 clause BSD licence 

# 
#  Tests for UnderFloor  nosetests TestUnderFloor.py
#

import sys, logging, time
import unittest

from MiscLib.DomHelpers  import *

from EventLib.Event import Event, makeEvent

from EventHandlers.BaseHandler import *
from EventHandlers.EventRouterLoad import EventRouterLoader

import EventHandlers.tests.TestEventLogger as TestEventLogger

import Events
from Utils import *

_log = logging
_log.basicConfig(level=logging.DEBUG, filename='TestUnderFloorHeating.log')


# Configuration for the tests
#
# this test uses the an event test a UnderFloor
#
testConfigUnderFloor = """<?xml version="1.0" encoding="utf-8"?>
<eventInterfaces>

    <eventInterface module='EventHandlers.tests.TestEventLogger' name='TestEventLogger'>
        <!-- This saves all events -->
        <eventtype type="">
            <eventsource source="" >
	        <event>
                    <!-- interested in all events -->
	        </event>
            </eventsource>
        </eventtype>
    </eventInterface>

    <eventInterface  module='EventHandlers.UnderFloorHeating' name='UnderFloorHeating' >
         <zone_temperature type='http://id.webbrick.co.uk/zones/zone' source='zone7/state' />  
         <run_event type='http://id.webbrick.co.uk/zones/zone' source='zone999/state' />  
         <stop_event type='http://id.webbrick.co.uk/zones/zone' source='zone999/stop' />  
         <air_temperature type='http://id.webbrick.co.uk/events/webbrick/CT' source='webbrick/100/CT/0' />  
         <floor_temperature type='http://id.webbrick.co.uk/events/webbrick/CT' source='webbrick/100/CT/1' />  

        <eventtype type="http://id.webbrick.co.uk/events/UnderFloor">
            <eventsource source="testing/UnderFloor">
                <event>
                    <newEvent type='testing' source='result/UnderFloor' />
                </event>
            </eventsource>
        </eventtype>



    </eventInterface>

</eventInterfaces>
"""



class TestUnderFloorAction(unittest.TestCase):

    def setUp(self):
        self._log = logging.getLogger( "TestUnderFloorAction" )
        self._log.debug(sys._getframe().f_code.co_name)

        self.router = None
        self.loader = None

    def tearDown(self):
        self._log.debug(sys._getframe().f_code.co_name)

        if self.loader:
            self.loader.stop()  # all tasks
            self.loader = None
        self.router = None
        time.sleep(2)

    def expectNevents(self, cnt ):
        idx = cnt + 5  # cope with more events that expected
        while (len(TestEventLogger._events) < cnt) and (idx > 0):
            time.sleep(0.05)
            idx = idx - 1

        if ( len(TestEventLogger._events) != cnt):
            TestEventLogger.logEvents()

        self.assertEqual( len(TestEventLogger._events), cnt)

    def common_set(self, target=20.0, air=19.0, floor=19.0 ):
        """
        http://id.webbrick.co.uk/zones/zone,zone7/state,{'status': 'Demand', 'actuatorstate': 2, 'manualsetpoint': None, 'zoneTemp': 16.300000000000001, 'weather1': 'Run', 'weather2': 'HoldOff', 'weather3': 'Run', 'weathercompensation': 1, 'cmdsource': 'Schedule', 'enabled': 1, 'wcselect': 1, 'schedulesetpoint': 19.0, 'state': 2, 'targetsetpoint': 19.0, 'zonesource': u'Electic UFH', 'minzonetemp': 9.0, 'occupied': 1, 'zoneenabled': '', 'followoccupancy': 0}
        """
        self.router.publish(EventAgent("TestUnderFloorAction"),makeEvent('http://id.webbrick.co.uk/zones/zone', 'zone999/state', {'targetsetpoint':target }))
        self.router.publish(EventAgent("TestUnderFloorAction"),makeEvent('http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/0', {'val':air }))
        self.router.publish(EventAgent("TestUnderFloorAction"),makeEvent('http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', {'val':floor }))
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtMinute10 )  # Create a minute that forces a check

    def display_events(self, e_list):
        lc = 0
        for e in e_list:
            print "Event %s Type %s  Source %s Payload %s" % (lc,  e.getType(), e.getSource(), e.getPayload())
            lc += 1

    # -----------------------------------------------------------------------------------------------------------------------------------
    # Actual tests follow
    def testUnderFloorStart(self):
        self._log.debug(sys._getframe().f_code.co_name)

        self.loader = EventRouterLoader()
        self.loader.loadHandlers( getDictFromXmlString(testConfigUnderFloor) )
        self.loader.start()  # all tasks
        self.router = self.loader.getEventRouter()
        self.common_set(air=15, floor=1)
        time.sleep(1)

        self.display_events(TestEventLogger._events)

        #self.expectNevents( 15 )
        self.assertEqual( TestEventLogger._events[2].getType(), u'http://id.webbrick.co.uk/events/UnderFloor' )
        self.assertEqual( TestEventLogger._events[2].getSource(), u"testing/UnderFloor" )
        self.assertEqual( TestEventLogger._events[2].getPayload()['output'], 100 )
        self.assertEqual( TestEventLogger._events[2].getPayload()['reason'], u"full demand" )

    def testUnderFloorStopEvent(self):
        self._log.debug(sys._getframe().f_code.co_name)

        self.loader = EventRouterLoader()
        self.loader.loadHandlers( getDictFromXmlString(testConfigUnderFloor) )
        self.loader.start()  # all tasks
        self.router = self.loader.getEventRouter()
        self.common_set(air=18, floor=40)
        time.sleep(1)

        self.display_events(TestEventLogger._events)

        self.assertEqual( TestEventLogger._events[2].getType(), u'http://id.webbrick.co.uk/events/UnderFloor' )
        self.assertEqual( TestEventLogger._events[2].getSource(), u"testing/UnderFloor" )
        self.assertEqual( TestEventLogger._events[2].getPayload()['output'], 0 )
        self.assertEqual( TestEventLogger._events[2].getPayload()['reason'], u"over temperature" )

    def testUnderFloorNormalStop(self):
        self._log.debug(sys._getframe().f_code.co_name)

        self.loader = EventRouterLoader()
        self.loader.loadHandlers( getDictFromXmlString(testConfigUnderFloor) )
        self.loader.start()  # all tasks
        self.router = self.loader.getEventRouter()
        self.common_set(air=21, floor=20)
        time.sleep(1)

        self.display_events(TestEventLogger._events)
        
        self.assertEqual( TestEventLogger._events[2].getType(), u'http://id.webbrick.co.uk/events/UnderFloor' )
        self.assertEqual( TestEventLogger._events[2].getSource(), u"testing/UnderFloor" )
        self.assertEqual( TestEventLogger._events[2].getPayload()['output'], 0 )
        self.assertEqual( TestEventLogger._events[2].getPayload()['reason'], u"air target reached" )

    def testUnderFloorHighEvent(self):
        self._log.debug(sys._getframe().f_code.co_name)

        self.loader = EventRouterLoader()
        self.loader.loadHandlers( getDictFromXmlString(testConfigUnderFloor) )
        self.loader.start()  # all tasks
        self.router = self.loader.getEventRouter()
        self.common_set(air=18, floor=40)
        time.sleep(1)

        self.display_events(TestEventLogger._events)

        self.assertEqual( TestEventLogger._events[2].getType(), u'http://id.webbrick.co.uk/events/UnderFloor' )
        self.assertEqual( TestEventLogger._events[2].getSource(), u"testing/UnderFloor" )
        self.assertEqual( TestEventLogger._events[2].getPayload()['output'], 0 )
        self.assertEqual( TestEventLogger._events[2].getPayload()['reason'], u"over temperature" )

    def testUnderFloorMid(self):
        self._log.debug(sys._getframe().f_code.co_name)

        self.loader = EventRouterLoader()
        self.loader.loadHandlers( getDictFromXmlString(testConfigUnderFloor) )
        self.loader.start()  # all tasks
        self.router = self.loader.getEventRouter()
        self.common_set(air=15, floor=27)
        time.sleep(1)
        
        self.assertEqual( TestEventLogger._events[2].getType(), u'http://id.webbrick.co.uk/events/UnderFloor' )
        self.assertEqual( TestEventLogger._events[2].getSource(), u"testing/UnderFloor" )
        self.assertEqual( TestEventLogger._events[2].getPayload()['output'], 50 )
        self.assertEqual( TestEventLogger._events[2].getPayload()['reason'], u"floor modulation" )

    def testUnderFloorAirMid(self):
        self._log.debug(sys._getframe().f_code.co_name)

        self.loader = EventRouterLoader()
        self.loader.loadHandlers( getDictFromXmlString(testConfigUnderFloor) )
        self.loader.start()  # all tasks
        self.router = self.loader.getEventRouter()
        self.common_set(air=19, floor=23)
        time.sleep(1)

        self.assertEqual( TestEventLogger._events[2].getType(), u'http://id.webbrick.co.uk/events/UnderFloor' )
        self.assertEqual( TestEventLogger._events[2].getSource(), u"testing/UnderFloor" )
        self.assertEqual( TestEventLogger._events[2].getPayload()['output'], 50 )
        self.assertEqual( TestEventLogger._events[2].getPayload()['reason'], u"air modulation" )


# Code to run unit tests directly from command line.
# Constructing the suite manually allows control over the order of tests.
def getTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestUnderFloorAction("testUnderFloorEvent"))

    return suite

from MiscLib import TestUtils
def getTestSuite(select="unit"):
    """
    Get test suite

    select  is one of the following:
            "unit"      return suite of unit tests only
            "component" return suite of unit and component tests
            "all"       return suite of unit, component and integration tests
            "pending"   return suite of pending tests
            name        a single named test to be run
    """
    testdict = {
        "unit": 
            [ "testUnderFloorStart" ,
              "testUnderFloorStopEvent" ,
              "testUnderFloorHighEvent" ,
              "testUnderFloorNormalStop" ,
              "testUnderFloorMid" ,
              "testUnderFloorAirMid" ,
            ]
        }
    return TestUtils.getTestSuite(TestUnderFloorAction, testdict, select=select)

# Run unit tests directly from command line
if __name__ == "__main__":
    TestUtils.runTests("TestUnderFloorAction.log", getTestSuite, sys.argv)

