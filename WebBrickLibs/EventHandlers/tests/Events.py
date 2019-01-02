# Copyright L.P.Klyne 2013 
# Licenced under 3 clause BSD licence 

# $Id: Events.py 3738 2010-10-01 15:04:17Z andy.harris $
#
# Some test Events
# 
import threading, sys, time

from EventLib.Event import Event, makeEvent

# Some test events that can be sent.

evtTD0 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/TD', 'webbrick/100/TD/0', {'tgtChannel': 0, 'srcChannel': 0, 'val': 1, 'setPoint': 0, 'fromNode': 100, 'udpType': 'G', 'version': 6, 'action': 1, 'dwell': 0, 'pktType': 'TD', 'ipAdr': '10.100.100.100'} )
evtTD1 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/TD', 'webbrick/100/TD/1', {'tgtChannel': 0, 'srcChannel': 0, 'val': 1, 'setPoint': 0, 'fromNode': 100, 'udpType': 'G', 'version': 6, 'action': 1, 'dwell': 0, 'pktType': 'TD', 'ipAdr': '10.100.100.100'} )
evtDO_0_off = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/DO', 'webbrick/100/DO/0', { 'state':'0' } )
evtDO_1_off = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/DO', 'webbrick/100/DO/1', { 'state':'0' } )
evtDO_2_off = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/DO', 'webbrick/100/DO/2', { 'state':'0' } )
evtDO_0_on = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/DO', 'webbrick/100/DO/0', { 'state':'1' } )
evtDO_1_on = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/DO', 'webbrick/100/DO/1', { 'state':'1' } )
evtDO_2_on = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/DO', 'webbrick/100/DO/2', { 'state':'1' } )
evtDI_0_off = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/DI', 'webbrick/100/DI/0', { 'state':'0' } )
evtDI_1_off = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/DI', 'webbrick/100/DI/1', { 'state':'0' } )
evtDI_0_on = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/DI', 'webbrick/100/DI/0', { 'state':'1' } )
evtDI_1_on = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/DI', 'webbrick/100/DI/1', { 'state':'1' } )

#
#  AnalogueIn events
#

evtAI_0_10 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/AI', 'webbrick/100/AI/0', { 'srcChannel': 0, 'curhi': 99.0, 'val': 10.0, 'fromNode': 100, 'curlo': 98.0, 'defhi': 99, 'deflo': 98} )

evtAI_0_90 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/AI', 'webbrick/100/AI/0', { 'srcChannel': 0, 'curhi': 99.0, 'val': 90.0, 'fromNode': 100, 'curlo': 98.0, 'defhi': 99, 'deflo': 98} )



evtSecond0 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1, 'week':2, 'hour': 4, 'minute':'1', 'second':'0', 'timestr':'04:01:00'} )
evtSecond1 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'1', 'timestr':'04:01:01' } )
evtSecond2 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'2', 'timestr':'04:01:02' } )
evtSecond3 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'3', 'timestr':'04:01:03' } )
evtSecond4 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'4', 'timestr':'04:01:04' } )
evtSecond5 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'5', 'timestr':'04:01:05' } )
evtSecond6 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'6', 'timestr':'04:01:06' } )
evtSecond7 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'7', 'timestr':'04:01:07' } )
evtSecond10 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'10', 'timestr':'04:01:10' } )
evtSecond15 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'15', 'timestr':'04:01:15' } )
evtSecond20 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'20', 'timestr':'04:01:20' } )
evtSecond25 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'25', 'timestr':'04:01:25' } )
evtSecond30 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'30', 'timestr':'04:01:30' } )
evtSecond35 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'35', 'timestr':'04:01:35' } )
evtSecond40 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'40', 'timestr':'04:01:40' } )
evtSecond45 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'45', 'timestr':'04:01:45' } )
evtSecond50 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'50', 'timestr':'04:01:50' } )
evtSecond55 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'1', 'second':'55', 'timestr':'04:01:55' } )
evtTimexx3030 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'30', 'second':'30', 'timestr':'04:30:30'  } )

evtRuntime5 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'5' } )
evtRuntime10 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'10' } )
evtRuntime15 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'15' } )
evtRuntime20 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'20' } )
evtRuntime25 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'25' } )
evtRuntime30 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'30' } )
evtRuntime35 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'35' } )
evtRuntime40 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'40' } )
evtRuntime45 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'45' } )
evtRuntime50 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'50' } )
evtRuntime55 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'55' } )
evtRuntime60 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'60' } )
evtRuntime65 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'65' } )
evtRuntime70 = makeEvent( 'http://id.webbrick.co.uk/events/time/runtime', 'time/runtime', { 'elapsed':'70' } )

evtMinute1 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':1, 'datestr': '2007-02-03', 'timestr':'04:01:00', 'datetimestr': '2007-02-03T04:01:00'} )
evtMinute2 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':2, 'datestr': '2007-02-03', 'timestr':'04:02:00', 'datetimestr': '2007-02-03T04:01:00'} )
evtMinute3 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':3, 'datestr': '2007-02-03', 'timestr':'04:03:00', 'datetimestr': '2007-02-03T04:01:00'} )
evtMinute4 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':4, 'datestr': '2007-02-03', 'timestr':'04:04:00', 'datetimestr': '2007-02-03T04:01:00'} )
evtMinute10 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':10, 'datestr': '2007-02-03', 'timestr':'04:10:00', 'datetimestr': '2007-02-03T04:01:00'} )
evtMinute11 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':11, 'datestr': '2007-02-03', 'timestr':'04:11:00', 'datetimestr': '2007-02-03T04:01:00'} )
evtMinute1Week3 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':3, 'hour': 4, 'minute':1, 'datestr': '2007-02-03', 'timestr':'04:01:00', 'datetimestr': '2007-02-03T04:01:00'} )
# TODO Add datsstr and datetimestr to the following time events.
evtMidnightMon = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 0, 'minute':0, 'datestr': '2007-02-03', 'timestr':'00:00:00'} )
evt0429 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 4, 'minute':29, 'datestr': '2007-02-03', 'timestr':'04:29:00'} )
evt0430 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 4, 'minute':30, 'datestr': '2007-02-03', 'timestr':'04:30:00'} )
evt0431 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 4, 'minute':31, 'datestr': '2007-02-03', 'timestr':'04:31:00'} )
evt0530 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 5, 'minute':30, 'datestr': '2007-02-03', 'timestr':'05:30:00'} )
evt0859 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 8, 'minute':59, 'datestr': '2007-02-03', 'timestr':'08:59:00'} )
evt0900 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 9, 'minute':0, 'datestr': '2007-02-03', 'timestr':'09:00:00'} )
evt0901 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 9, 'minute':1, 'datestr': '2007-02-03', 'timestr':'09:01:00'} )
evt1629 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 16, 'minute':29, 'datestr': '2007-02-03', 'timestr':'16:29:00'} )
evt1630 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 16, 'minute':30, 'datestr': '2007-02-03', 'timestr':'16:30:00'} )
evt1631 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 16, 'minute':31, 'datestr': '2007-02-03', 'timestr':'16:31:00'} )
evt2159 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 21, 'minute':59, 'datestr': '2007-02-03', 'timestr':'21:59:00'} )
evt2200 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 22, 'minute':0, 'datestr': '2007-02-03', 'timestr':'22:00:00'} )
evt2201 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 22, 'minute':1, 'datestr': '2007-02-03', 'timestr':'22:01:00'} )

evt0000 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 0, 'minute':0, 'datestr': '2007-02-03', 'timestr':'00:00:00'} )
evt0100 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 1, 'minute':0, 'datestr': '2007-02-03', 'timestr':'01:00:00'} )
evt0200 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 2, 'minute':0, 'datestr': '2007-02-03', 'timestr':'02:00:00'} )
evt0300 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 3, 'minute':0, 'datestr': '2007-02-03', 'timestr':'03:00:00'} )
evt0400 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 4, 'minute':0, 'datestr': '2007-02-03', 'timestr':'04:00:00'} )
evt0500 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 5, 'minute':0, 'datestr': '2007-02-03', 'timestr':'05:00:00'} )
evt0600 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 6, 'minute':0, 'datestr': '2007-02-03', 'timestr':'06:00:00'} )
evt0700 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 7, 'minute':0, 'datestr': '2007-02-03', 'timestr':'07:00:00'} )
evt0800 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 8, 'minute':0, 'datestr': '2007-02-03', 'timestr':'08:00:00'} )
evt0900 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 9, 'minute':0, 'datestr': '2007-02-03', 'timestr':'09:00:00'} )
evt1000 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 10, 'minute':0, 'datestr': '2007-02-03', 'timestr':'10:00:00'} )
evt1100 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 11, 'minute':0, 'datestr': '2007-02-03', 'timestr':'11:00:00'} )
evt1200 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 12, 'minute':0, 'datestr': '2007-02-03', 'timestr':'12:00:00'} )
evt1300 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 13, 'minute':0, 'datestr': '2007-02-03', 'timestr':'13:00:00'} )
evt1400 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 14, 'minute':0, 'datestr': '2007-02-03', 'timestr':'14:00:00'} )
evt1500 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 15, 'minute':0, 'datestr': '2007-02-03', 'timestr':'15:00:00'} )
evt1600 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 16, 'minute':0, 'datestr': '2007-02-03', 'timestr':'16:00:00'} )
evt1700 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 17, 'minute':0, 'datestr': '2007-02-03', 'timestr':'17:00:00'} )
evt1800 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 18, 'minute':0, 'datestr': '2007-02-03', 'timestr':'18:00:00'} )
evt1900 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 19, 'minute':0, 'datestr': '2007-02-03', 'timestr':'19:00:00'} )
evt2000 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 20, 'minute':0, 'datestr': '2007-02-03', 'timestr':'20:00:00'} )
evt2100 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 21, 'minute':0, 'datestr': '2007-02-03', 'timestr':'21:00:00'} )
evt2200 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 22, 'minute':0, 'datestr': '2007-02-03', 'timestr':'22:00:00'} )
evt2300 = makeEvent( 'http://id.webbrick.co.uk/events/time/minute', 'time/minute', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'hour': 23, 'minute':0, 'datestr': '2007-02-03', 'timestr':'23:00:00'} )

evtDark = makeEvent( 'http://id.webbrick.co.uk/events/time/isDark', 'time/isDark', { 'state':1 } )
evtLight = makeEvent( 'http://id.webbrick.co.uk/events/time/isDark', 'time/isDark', { 'state':0 } )

evtHour03 = makeEvent( 'http://id.webbrick.co.uk/events/time/hour', 'time/hour', { 'year': 2007, 'month': 2, 'date': 3, 'day':1, 'hour':3, 'timestr':'03:00:00' } )

evtAI_1_50 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/AI', 'webbrick/100/AI/1', { 'val':50 } )
evtAI_1_50_plus_params = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/AI', 'webbrick/100/AI/1', { 'val':50, 'preoffset':30, 'postoffset':30, 'multiplier':3,  } )
evtAI_1_60_plus_params = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/AI', 'webbrick/100/AI/1', { 'val':60, 'preoffset':0, 'postoffset':0, 'multiplier':1, 'divisor':10,  } )


evtCT_1_25 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', { 'val':25 } )

evtSS = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/SS', 'webbrick/100/SS', { 'ipAdr':'localhost:20999' } )

evtST_1MinUpTime = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/ST', 'webbrick/100/ST', 
             { 'uptime':1, 'resetCode': 123, 'hour': 1, 'minute':1, 'second':1, 'day':1, 'ipAdr':'127.0.0.1:20999'} )

evtST_10MinUpTime = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/ST', 'webbrick/100/ST', 
             { 'uptime':6, 'resetCode': 123, 'hour': 1, 'minute':1, 'second':1, 'day':1, 'ipAdr':'127.0.0.1:20999'} )


# Events for testing new features of Value convert

evtHEX_0 = makeEvent( 'value/hex_to_dec', 'testing/converion/hex_to_dec', { 'val':'0' } )
evtHEX_32 = makeEvent( 'value/hex_to_dec', 'testing/converion/hex_to_dec', { 'val':'32' } )
evtHEX_64 = makeEvent( 'value/hex_to_dec', 'testing/converion/hex_to_dec', { 'val':'64' } )
        
evtINT_0  = makeEvent( 'value/dec_to_hex', 'testing/converion/dec_to_hex', { 'val':'0' } )
evtINT_50  = makeEvent( 'value/dec_to_hex', 'testing/converion/dec_to_hex', { 'val':'50' } )
evtINT_100 = makeEvent( 'value/dec_to_hex', 'testing/converion/dec_to_hex', { 'val':'100' } )

#Events for testing features of Timer

evtTimerConEnable = makeEvent( 'http://id.webbrick.co.uk/events/config/get', 'test/timer/1/enable', { 'val':'True' } )
evtTimerConDisable = makeEvent( 'http://id.webbrick.co.uk/events/config/get', 'test/timer/1/enable', { 'val':'0' } )
evtTimerConDuration = makeEvent( 'http://id.webbrick.co.uk/events/config/get', 'test/timer/1/duration', { 'val':'3' } )

evtHome = makeEvent( 'http://id.webbrick.co.uk/events/config/get', 'occupants/home', { 'val':'1' } )
evtAway = makeEvent( 'http://id.webbrick.co.uk/events/config/get', 'occupants/home', { 'val':'0' } )

evtMorningDark = makeEvent( 'http://id.webbrick.co.uk/events/time/dayphaseext', 'time/dayphaseext', { 'dayphasetext':'Morning:Dark' } )

# Events for testing SolarRun


evtSolarRunConEnable = makeEvent( 'http://id.webbrick.co.uk/events/config/get', 'test/SolarRun/1/enable', { 'val':'True' } )
evtSolarRunConDisable = makeEvent( 'http://id.webbrick.co.uk/events/config/get', 'test/SolarRun/1/enable', { 'val':'False' } )
evtSolarRunConCheckTime = makeEvent( 'http://id.webbrick.co.uk/events/config/get', 'test/SolarRun/1/check_time', { 'val':'10' } )   # in minutes
evtSolarRunConCheckRunTime = makeEvent( 'http://id.webbrick.co.uk/events/config/get', 'test/SolarRun/1/check_run_time', { 'val':'2' } ) # in seconds

evtMorningLight = makeEvent( 'http://id.webbrick.co.uk/events/time/dayphaseext', 'time/dayphaseext', { 'dayphasetext':'Morning:Light' } )

evtCT_0_15 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/0', { 'val':15 } )
evtCT_0_19 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/0', { 'val':19 } )
evtCT_0_20 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/0', { 'val':20 } )
evtCT_0_25 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/0', { 'val':25 } )
evtCT_0_27 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/0', { 'val':27 } )
evtCT_0_30 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/0', { 'val':30 } )
evtCT_0_50 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/0', { 'val':50 } )
evtCT_0_75 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/0', { 'val':75 } )
evtCT_0_80 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/0', { 'val':80 } )
evtCT_0_85 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/0', { 'val':85 } )
evtCT_0_90 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/0', { 'val':90 } )

evtCT_1_15 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', { 'val':15 } )
evtCT_1_19 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', { 'val':19 } )
evtCT_1_20 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', { 'val':20 } )
evtCT_1_25 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', { 'val':25 } )
evtCT_1_27 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', { 'val':27 } )
evtCT_1_30 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', { 'val':30 } )
evtCT_1_50 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', { 'val':50 } )
evtCT_1_75 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', { 'val':75 } )
evtCT_1_80 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', { 'val':80 } )
evtCT_1_85 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', { 'val':85 } )
evtCT_1_90 = makeEvent( 'http://id.webbrick.co.uk/events/webbrick/CT', 'webbrick/100/CT/1', { 'val':90 } )

evtSecond180 = makeEvent( 'http://id.webbrick.co.uk/events/time/second', 'time/second', { 'year': 2007, 'month': 2, 'date': 3, 'day': 1,'week':2, 'hour': 4, 'minute':'3', 'second':'55', 'timestr':'04:03:55' } )









        
