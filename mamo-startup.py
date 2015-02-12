import clr

clr.AddReference("PacBio.Instrument.Interfaces.RunControl")
from PacBio.Instrument.Interfaces.RunControl import *

from PacBio.Instrument.Homer import *
from PacBio.Instrument.Interfaces import *
from PacBio.Instrument.Interfaces.Homer import *
from System.Collections import *

import sys
import time

def HomerStateTransition(obj, state):
    print "-----------------------> State Transition:", InstrumentContext.Instrument.FSM.CurrentState    
    

try:
    
    instrument = InstrumentContext.Instrument
    chipTipDrawer = instrument.ChipsTipsDrawer	
    tempDrawer = instrument.TemplateReagentDrawer    
    runner = instrument.RunController
    alarmPublisher = instrument.FakeAlarmPublisher
    alarmManager = instrument.AlarmManagerSvc    

    instrument.FSM.StateTransition += HomerStateTransition
        

except:
	print "Unexpected error:", sys.exc_info()[0]
	raise

#Pass None for a null barcode
def UpdateTestSamplePlate(plateBarcode): 
    tempDrawer.TemplateBarcodeScanner.TEST_Barcode(plateBarcode)
    tempDrawer.Open()
    tempDrawer.Close()

def UploadDB(file='c:/sandbox/Manny/newSS.csv'):
    execfile('Protocols/importSS.py')
    instrument.SampleSheetSvc.SampleSheetImport(file)
  
def InventoryScan():
    runner.InventoryScan()
    
def LockDrawers(locked):
     instrument.TemplateReagentDrawer.Locked = locked
     instrument.ChipsTipsDrawer.Locked = locked 

def PublishAlarm(name, severity):
    alarmPublisher.PublishAlarm(name, "test", severity)

def ClearAlarms():
    for alarm in alarmManager.SystemAlarms:
        alarm.Severity = AlarmSeverity.CLEAR

def ListAlarms():
    for alarm in alarmManager.SystemAlarms:
        print alarm.Name, " Alarm Severity: ", alarm.Severity

       
    
