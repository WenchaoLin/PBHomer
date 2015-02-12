import clr

clr.AddReference("PacBio.Instrument.Interfaces.RunControl")

from System.Collections import *

from PacBio.Common.Diagnostics import *

from PacBio.Instrument.Interfaces.RunControl import *
from PacBio.Instrument.Homer import *
from PacBio.Instrument.Interfaces import *
from PacBio.Instrument.Interfaces.Homer import *
from PacBio.Instrument.Interfaces.Vision import *
from PacBio.Instrument.Protocols import *

#from protocols import *


import sys
import time

logger = DiagManager.LogManager.LocalLogger("Python." + __name__)

def sanityCfg():
    """ stuff changed for sanity so it doesn't take too long"""
    i=InstrumentContext.Instrument
    cas = i.ChipAlignment
    cas.AlignParams.StageLevelParams.StepsPerStack = 1
    cas.AlignParams.StageLevelParams.MaxIterations = 1

def UseDefaultBarcodes():
    inst = InstrumentContext.Instrument
    drawer = inst.TemplateReagentDrawer
    drawer.SetManualBarcode(MVLocationName.SamplePlate, "ABC01234")
    drawer.SetManualBarcode(MVLocationName.ReagentPlate0, "004012725000326298091311")
    drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "0", "004012345000655229091511")
    drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "1", "004012346000655229091511")
    drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "0", "004012347000655229091511")
    drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "1", "004012348000655229091511")
    chips = inst.ChipsTipsDrawer
    chips.SetManualBarcode(MVLocationName.ChipStrip + "-0", "004012725000640618121511")
    # add more if we need them... the value after the 5 varies...
    
# Load and run an acquisition protocol
try:
    # no longer needed - we wait for instrument to boot before runing sanity
    # print "Waiting 30 secs for system to finish boot..."
    # time.sleep(30)

    i=InstrumentContext.Instrument
    
    #seed DB if it isnot seeded already
    #comment out these lines, the DB will be seeded before Homer makes the first contact
    #SMgr = i.DataSeedingManagerSvc
    #SMgr.SeedDB()
    
    #some mods for sanity sake
    #sanityCfg()
    
    executor = i.ProtocolExecutor
    ProtocolLiquidToolKit.RealPauses = False
    
    UseDefaultBarcodes()
    i.TemplateReagentDrawer.SnapshotSamplePlateState()
    #i.TemplateReagentDrawer.SetManualBarcode(MVLocationName.SamplePlate, samplePlate)
    i.DrawerOracle.AddPointIfLocationMissing(MVLocationName.MixingPlate)
    
    scanResult = executor.InventoryScan()
    logger.Log(ScriptingLogEvent("inventory scan result:" + scanResult.FailureMessage))
    
    loadResult = executor.LoadProtocol("SMSReagentMixingProtocol_DWP")
    logger.Log(ScriptingLogEvent("protocol load result:" + loadResult.LoadedProtocolIdentifier))
    
    d = { }
    params = executor.GetProtocolParameters()
    for pname in params.Keys:
        d[pname] = params[pname]

    exeResult = executor.Execute(d)

    logger.Log(ScriptingLogEvent('reagent protocol result:'+ exeResult.FailureMessage))
    
    loadResult = executor.LoadProtocol("DefaultCollectionProtocol")
    logger.Log(ScriptingLogEvent("protocol load result:"+ loadResult.LoadedProtocolIdentifier))

    d = { }
    params = executor.GetProtocolParameters()
    for pname in params.Keys:
        d[pname] = params[pname]

    exeResult = executor.Execute(d)

    logger.Log(ScriptingLogEvent('collection protocol result:'+ exeResult.FailureMessage))

    #loadResult = executor.LoadProtocolFile("SqwatAcquisitionProtocol.py")
    #logger.Log(ScriptingLogEvent("protocol load result:"+ loadResult.LoadedProtocolIdentifier))

    #d = { }
    #params = executor.GetProtocolParameters()
    #for pname in params.Keys:
    #    d[pname] = params[pname]

    #exeResult = executor.Execute(d)

    #logger.Log(ScriptingLogEvent('Sqwat acquisition protocol result:'+ exeResult.FailureMessage))


except:
    #logger.Log(ExceptionLogEvent("Unexpected error in sanity:" + sys.exc_info()[0]))
    raise
    
    
