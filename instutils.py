#
#instrument utils
#   
import clr
import os
import sys
import System

from instrumentGlobals import *

# for System.Web.Script which lives in the extensions library
clr.AddReference("System.Web.Extensions")

def dumpAllShort():
    """Show a brief dump of instrument state"""
    from PacBio.Common.Services import *
    ServiceUtil.ShowTree(instrument)

def dumpAllAlarmsBrief():
    """Show a brief dump of all pending alarms"""
    DumpUtil.DumpContents(System.Console.Out, instrument.AlarmManagerSvc.SystemAlarms, 100)

def dumpAllAlarms(severity=None):
    """Show a more detailed dump of all pending alarms"""
    print 'Alarms (verbose):'
    print ''
    current = instrument.AlarmManagerSvc.SystemAlarms
    if current.Length == 0:
        print '  No alarms'
        print ''
    for x,alarm in enumerate(current):
        clearaging = ""
        raiseaging = ""
        aging = ""
        if(alarm.AgingWhenLowering != System.TimeSpan.Zero):
            clearaging = ' %s min to lower' % (alarm.AgingWhenLowering.TotalMinutes.ToString())
        if(alarm.AgingWhenRaising != System.TimeSpan.Zero):
            raiseaging = ' %s min to raise' % (alarm.AgingWhenRaising.TotalMinutes.ToString())
        if((clearaging is not "") or (raiseaging is not "")):
            aging = ' [Takes%s%s]' % (clearaging, raiseaging)
        if(severity is None or severity == alarm.Severity):
            print '  %d= %s %s %s\n' % (x, alarm, System.Web.Script.Serialization.JavaScriptSerializer().Serialize(alarm.Info), aging)
    aging = instrument.AlarmManagerSvc.AgingAlarms
    if aging.Count != 0:
        print 'The following alarms are about to change. They are aging:'
        for x,item in enumerate(aging):
            enabled = item.Timer.Enabled
            remainingMinutes = item.Timer.Remaining.TotalMilliseconds / 60000
            if enabled:
                print ' %d= Alarm(%s): %s, %s in %s minutes' % (x, item.Alarm.Owner, item.Alarm.Severity, item.Alarm.Name, remainingMinutes)
    squelched = instrument.AlarmManagerSvc.Squelched
    if squelched.Count != 0:
        print 'Warning: The following alarms have been squelched either temporarily or persistently:'
        for x,item in enumerate(squelched):
            persist = ''
            if item.Persistant:
                persist = ' persistantly'
            print '  %d= %s (%s) squelched%s to %s because: %s' % (x, item.Name, item.Source, persist, item.MaxSeverity, item.Reason)
        print ''

def dumpServiceAlarms(svc, severity=AlarmSeverity.WARNING):
    dumpList(svc.GetServiceAlarms(severity))

def dumpPerfMons():
    """Show a brief dump of registered, periodic perfmons"""
    from PacBio.Common.PerfMon import *
    current = PerfMonRegistrar.GetPeriodicPerfMons()
    for i,perf in enumerate(current):
        print '  %d= %s  Interval: %s' % (i, perf.ShortName.rjust(28), str(perf.Interval).ljust(10))

def dumpAllPerfMons():
    dumpPerfMons()

def dumpAllDiags():
    """Show a brief dump of diags status"""
    from PacBio.Instrument.Devices import *
    DeviceBase.ShowDiagStatus(instrument)

def dumpThresholds(monitor):
    count = 0
    order = [AlarmThresholds.FATAL_IMMEDIATE_LOW, AlarmThresholds.FATAL_LOW,  AlarmThresholds.CRITICAL_LOW,  AlarmThresholds.ERROR_LOW,  AlarmThresholds.WARNING_LOW, AlarmThresholds.WARNING_HIGH,   AlarmThresholds.ERROR_HIGH,   AlarmThresholds.CRITICAL_HIGH,   AlarmThresholds.FATAL_HIGH,   AlarmThresholds.FATAL_IMMEDIATE_HIGH]
    print '(Low->High):'.rjust(30),
    for o in order:
        value = monitor.GetThreshold(o)
        if (count == 5):
            print " | ",
        count = count + 1
        if (value > 1.7e+308):
            print "Max".ljust(7),
            continue
        if (value < -1.7e+308):
            print "Min".ljust(7),
            continue
        print str(value).ljust(7),
    print ''

def dumpAllMonitors():
    """Show a dump of environmental monitors"""
    from PacBio.Instrument.Diagnostics import *
    print ''
    anyOverrides = False
    monitors = MonitorSvc.GetInstance.All
    for monitor in monitors:
        name = monitor.Device.ToString()
        if monitor.DeclOverridden:
            name = "* " + name 
            anyOverrides = True
        print name.rjust(28),
        try:
            shouldbe = monitor.AlarmSeverityAtCurrentValue().ToString()
            if not monitor.Enabled:
                shouldbe = "(disabled)"
            print ':', monitor.Value.ToString().ljust(21), 'Alarm:'.rjust(16), shouldbe
            dumpThresholds(monitor)
        except:
            print 'Exception...'.rjust(24)
        print ''
    if anyOverrides is True:
        print ''.rjust(30) + ' (*) some monitor settings overridden by instrument Decl data'
        print ''

def dumpToFile():
    """Dump the entire instrument state to an XML file"""
    fname = instrument.DebugDumpToFile()
    print "Instrument debug file dumped to: ", fname

def dumpList(list):
    for i,item in enumerate(list):
        print i,": ",item.ToString()

def updateDB():
    print "THIS CALL HAS BEEN DEPRECATED"
    print 'PLEASE USE THE OBJECT BROWSER OR THE COMMAND: <svc>.UpdateRepository("<item>")'
    #"""Dump the entire instrument state back to the DB"""
    #instrument.UpdateRepository(DeclDataClassification.Any, True)
    
def exportDB(basename):
    """Dump the entire instrument state back to the DB & export via xml (config/decldata etc...)"""
    #updateDB()
    print "Exporting as ", basename + ".cfg.xml and " + basename + ".cal.xml"
    instrument.DataMigrationSvc.ExportConfigurationData(basename + ".cfg.xml")
    instrument.DataMigrationSvc.ExportCalibrationData(basename + ".cal.xml")
    
def importDB(basename):
    """Read a XML serialization to fill the DB"""
    print "Importing from ", basename
    instrument.DataMigrationSvc.ImportConfigurationData(basename + ".cfg.xml")
    instrument.DataMigrationSvc.ImportCalibrationData(basename + ".cal.xml")
    
def printSvcTree(svc=instrument, depth=0):
    """Print tree of Services, starting with instrument (or provide a Service)"""
    print ('    ')*depth, svc.FullName	
    for child in svc.Children:
        printSvcTree(child.Value, depth+1)
