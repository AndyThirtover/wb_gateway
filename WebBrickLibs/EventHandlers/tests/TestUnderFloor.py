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

    <eventInterface  module='EventHandlers.UnderFloor' name='UnderFloor' >
         <zone_temperature type='http://id.webbrick.co.uk/zones/zone' source='zone7/state' />  
         <run_event type='http://id.webbrick.co.uk/zones/zone' source='zone999/run' />  
         <stop_event type='http://id.webbrick.co.uk/zones/zone' source='zone999/stop' />  
         <air_temperature type='http://id.webbrick.co.uk/events/webbrick/CT' source='webbrick/999/CT/0' />  
         <floor_temperature type='http://id.webbrick.co.uk/events/webbrick/CT' source='webbrick/999/CT/1' />  

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
        idx = 20
        while (len(TestEventLogger._events) < cnt) and (idx > 0):
            time.sleep(0.05)
            idx = idx - 1

        if ( len(TestEventLogger._events) != cnt):
            TestEventLogger.logEvents()

        self.assertEqual( len(TestEventLogger._events), cnt)

    def common_set(self,pump=False, air='Cold', floor='Normal' ):
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond0 )  # Create a 'second'
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond1 )  # Create a 'second'
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond2 )  # Create a 'second'
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtMinute10 )  # Create a minute that forces a check
        if air == 'Cold':
            self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtCT_0_15 )  # Air Temp
        else:
            self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtCT_0_25 )  # Air Temp
        if floor == 'Normal':            
            self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtCT_1_19 )  # Floor Temp
        else:
            self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtCT_1_30 )  # Floor Over Temp

        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond4 )  # Create a 'second'

    def display_events(self, e_list):
        lc = 0
        for e in e_list:
            print "Event %s Type %s  Source %s Payload %s" % (lc,  e.getType(), e.getSource(), e.getPayload())
            lc += 1

    # Actual tests follow
    def testUnderFloorStart(self):
        self._log.debug(sys._getframe().f_code.co_name)

        self.loader = EventRouterLoader()
        self.loader.loadHandlers( getDictFromXmlString(testConfigUnderFloor) )
        self.loader.start()  # all tasks
        self.router = self.loader.getEventRouter()
        self.common_set(pump=False, air='Cold', floor='Normal')
        time.sleep(1)

        self.display_events(TestEventLogger._events)

        self.expectNevents( 15 )
        self.assertEqual( TestEventLogger._events[10].getType(), u'http://id.webbrick.co.uk/events/UnderFloor' )
        self.assertEqual( TestEventLogger._events[10].getSource(), u"testing/UnderFloor" )



    def testUnderFloorStopEvent(self):
        self._log.debug(sys._getframe().f_code.co_name)

        self.loader = EventRouterLoader()
        self.loader.loadHandlers( getDictFromXmlString(testConfigUnderFloor) )
        self.loader.start()  # all tasks
        self.router = self.loader.getEventRouter()
        self.common_set(pump=True, air='Cold', floor='Normal')
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond5 )  # Create a 'second'
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond6 )  # Create a 'second'
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond7 )  # Create a 'second'
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtCT_1_50 )  # Tank Temp
        time.sleep(1)

        #self.display_events(TestEventLogger._events)

        self.expectNevents( 21 )
        
        self.assertEqual( TestEventLogger._events[19].getType(), u'http://id.webbrick.co.uk/events/UnderFloor' )
        self.assertEqual( TestEventLogger._events[19].getSource(), u"testing/UnderFloor" )


    def testUnderFloorNormalStop(self):
        self._log.debug(sys._getframe().f_code.co_name)

        self.loader = EventRouterLoader()
        self.loader.loadHandlers( getDictFromXmlString(testConfigUnderFloor) )
        self.loader.start()  # all tasks
        self.router = self.loader.getEventRouter()
        self.common_set(pump=False, air='Hot', floor='Normal')
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtCT_0_80 )  # Pipe Temp
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond5 )  # Create a 'second'
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond6 )  # Create a 'second'
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond7 )  # Create a 'second'
        time.sleep(1)

        
        self.assertEqual( TestEventLogger._events[14].getType(), u'http://id.webbrick.co.uk/events/UnderFloor' )
        self.assertEqual( TestEventLogger._events[14].getSource(), u"testing/UnderFloor" )
        self.assertEqual( TestEventLogger._events[14].getPayload()['set_pump_state'], u"run" )

    def testUnderFloorHighEvent(self):
        self._log.debug(sys._getframe().f_code.co_name)

        self.loader = EventRouterLoader()
        self.loader.loadHandlers( getDictFromXmlString(testConfigUnderFloor) )
        self.loader.start()  # all tasks
        self.router = self.loader.getEventRouter()
        self.common_set(pump=True, air='Hot', floor='Over')
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtCT_0_80 )  # Pipe Temp
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond5 )  # Create a 'second'
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond6 )  # Create a 'second'
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond7 )  # Create a 'second'
        time.sleep(1)

        #self.display_events(TestEventLogger._events)

        self.expectNevents( 21 )
        
        self.assertEqual( TestEventLogger._events[16].getType(), u'http://id.webbrick.co.uk/events/UnderFloor' )
        self.assertEqual( TestEventLogger._events[16].getSource(), u"testing/UnderFloor" )
        self.assertEqual( TestEventLogger._events[16].getPayload()['set_pump_state'], u"stop" )


    def testUnderFloorMid(self):
        self._log.debug(sys._getframe().f_code.co_name)

        self.loader = EventRouterLoader()
        self.loader.loadHandlers( getDictFromXmlString(testConfigUnderFloor) )
        self.loader.start()  # all tasks
        self.router = self.loader.getEventRouter()
        self.common_set(pump=True, air='Cool', floor='Normal')
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtCT_1_27 )  # Floor Temp
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond5 )  # Create a 'second'
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtMinute1 )  # Create a 'minute'
        time.sleep(1)
        
        self.assertEqual( TestEventLogger._events[19].getType(), u'http://id.webbrick.co.uk/events/UnderFloor' )
        self.assertEqual( TestEventLogger._events[19].getSource(), u"testing/UnderFloor" )
        self.assertEqual( TestEventLogger._events[19].getPayload()['set_pump_state'], u"stop" )


    def testUnderFloorAirMid(self):
        self._log.debug(sys._getframe().f_code.co_name)

        self.loader = EventRouterLoader()
        self.loader.loadHandlers( getDictFromXmlString(testConfigUnderFloor) )
        self.loader.start()  # all tasks
        self.router = self.loader.getEventRouter()
        self.common_set(pump=True, air='Cool', floor='Normal')
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtCT_0_19 )  # Air Temp
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtCT_1_25 )  # Floor Temp
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtSecond5 )  # Create a 'second'
        time.sleep(1)
        self.router.publish( EventAgent("TestUnderFloorAction"), Events.evtMinute1 )  # Create a 'minute'
        time.sleep(1)
        
        self.assertEqual( TestEventLogger._events[19].getType(), u'http://id.webbrick.co.uk/events/UnderFloor' )
        self.assertEqual( TestEventLogger._events[19].getSource(), u"testing/UnderFloor" )
        self.assertEqual( TestEventLogger._events[19].getPayload()['set_pump_state'], u"stop" )





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
            ],
        "zzcomponent":
            [ "testComponents"
            ],
        "zzintegration":
            [ "testIntegration"
            ],
        "zzpending":
            [ "testPending"
            ]
        }
    return TestUtils.getTestSuite(TestUnderFloorAction, testdict, select=select)

# Run unit tests directly from command line
if __name__ == "__main__":
    TestUtils.runTests("TestUnderFloorAction.log", getTestSuite, sys.argv)

