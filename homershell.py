#
# Homer shell startup script
#
# Warning: This script is not necessarily run on start of the instrument,
# it is only run when a shell terminal/console is started.
#
# Warning: This is run anytime a script shell is started, so this can be run
# multiple times on any instrument. DO NOT ADD any kind of configuration or
# actionable code here. Only define functions and globals helpful for a shell.
# 
# If you have an action that should run on start for each instrument
#
# 1) Consider if it should be part of composition or configuration of a service
# 2) Reconsider #1 one more time
# 3) Otherwise put it in "startactions.py" instead of here
#
# We should audit this script now and then to ensure that it only defines
# macros and globals and doesn't perform any kind of action, including all
# scripts that it includes.
#

import clr
import os
import sys
import time

#.Net useful stuff
from System import TimeSpan
from System.IO import Path
from System.Reflection import Assembly

#PBI useful stuff
from PacBio.Instrument.Homer import *
from PacBio.Instrument.Interfaces import *
from PacBio.Instrument.Interfaces.Alignment import *
from PacBio.Instrument.Interfaces.Loader import *
from PacBio.Instrument.Interfaces.Homer import *
from PacBio.Instrument.Interfaces.Movement import *

from PacBio.Common.Diagnostics import *
from PacBio.Common.Numeric.Units import *
from PacBio.Common.Utils import ReflectionUtils
from PacBio.Common.Frames import *
from PacBio.Common.Data.Decl import *
from PacBio.Common.IO import *
from PacBio.Instrument.Alignment import *
from PacBio.Instrument.Alignment.Core import *
from PacBio.Instrument.Alignment.Analyzers import *
from PacBio.Instrument.Alignment.Utils import *
clr.AddReference("PacBio.Instrument.Alignment.Aligners")
from PacBio.Instrument.Alignment.Aligners import *
from PacBio.Instrument.Halcon import *
from PacBio.Common.Movie import *

clr.AddReference("HomerApp")
from HomerApp import *

# BSBR useful stuff
clr.AddReference("PacBio.Instrument.BSBR")
from PacBio.Instrument.BSBR import *

# Application Configuration
clr.AddReference("PacBio.Instrument.ApplicationConfiguration")
from PacBio.Instrument.ApplicationConfiguration import *

logger = DiagManager.LogManager.LocalLogger("HomerShell.")

logger.Log(ProgramLogEvent("Loading PacBio homerstartup.py debug environment..."))

def AddPath():
    pds = str(Path.DirectorySeparatorChar)
    exedir = Path.GetDirectoryName(Assembly.GetEntryAssembly().Location)
    pbiDir = exedir + ( pds + ( (".."+pds)*3 ))

    sys.path.append(Program.CompositionDir)
    sys.path.append(Program.ScriptsDir)
    sys.path.append(Program.CannedScriptsDir)
    sys.path.append(Program.ProtocolsDir)
    cannedScriptDir = Program.CannedScriptsDir

    # Add all the subdirectories of the cannedScripts dir too.
    for item in os.listdir(cannedScriptDir):
        itemPath = os.path.join(cannedScriptDir, item)
        if os.path.isdir(itemPath):
            sys.path.append(itemPath)

    # Need to add the InstrumentTest/src and InstrumentTests/tests to the path for tests automation
    instrumentTestsDir = os.path.join(cannedScriptDir, "InstrumentTests")
    if not os.path.exists(instrumentTestsDir):
        instrumentTestsDir = os.path.join(exedir, "canned_scripts", "InstrumentTests")
    if os.path.exists(instrumentTestsDir) and os.path.isdir(instrumentTestsDir):
        insttestsDirs = ('src', 'tests')
        for onedir in insttestsDirs:
            insttestsSrcPath = os.path.join(instrumentTestsDir, onedir)
            if (os.path.isdir(insttestsSrcPath)):
                sys.path.append(insttestsSrcPath)
                	
    # quite nasty robocal hack follows
    p4rootDir = exedir + pds + ".." + pds + ".." + pds + ".." + pds + ".." + pds + ".." + pds
    roboCalDir =  p4rootDir + "Integration" + pds + "Springfield" + pds + "Robotics" + pds + "RoboCal"
    if (os.path.isdir(roboCalDir)):
        sys.path.append(roboCalDir)

AddPath()

# inst utils were moved into their own file
from instutils import *

#
# test routines for robot
#

def chipToStage( g=Gripper.Gripper1, swatChipLoc=0 ):
    """Move a chip from jig to the stage (disposing of any chip already on the stage)"""
    try:
        chipCheck=r.RobotToStage.NoCheckForChip
        curAxisType=stage.CurrentAxisType
        stage.CurrentAxisType=StageAxisType.Coarse
        stage.Axis.TargetPosition=(0,0,0,0,0,0)
        MovementException.CheckWaitForMove(stage.Axis)
        r.RobotToStage.NoCheckForChip=True
        r.PickupChipFromStage(g)
        r.DisposeChip(g)
        r.CalibrateGripperToStage(g)
        r.PickupChip(g, InstrumentLocation("TestJigChip-" + str(swatChipLoc) ) )
        r.MoveChipToStage(g, True)
    except:
        raise
    finally:
        stage.CurrentAxisType=curAxisType
        r.RobotToStage.NoCheckForChip=chipCheck

def chipFromStage( g=Gripper.Gripper1, swatChipLoc=0 ):
    """Move a chip from the stage to the jig"""
    try:
        curAxisType=stage.CurrentAxisType
        stage.CurrentAxisType=StageAxisType.Coarse
        stage.Axis.TargetPosition=(0,0,0,0,0,0)
        MovementException.CheckWaitForMove(stage.Axis)
        r.PickupChipFromStage(g)
        r.PlaceChip(g, InstrumentLocation("TestJigChip-" + str(swatChipLoc) ) )
    except:
        raise
    finally:
        stage.CurrentAxisType=curAxisType

#
# Create standard globals
#

from instrumentGlobals import *

#=====================
# other useful scripts
# may rely on our sys.path being setup and that globals are already defined

from calibration import *
from AcquisitionUtils import *
from StageUtils import *
from AlignmentUtils import *
from TW import *
from CQ import *

#=====================


#=====================
# log filtering
#=====================
#To see all filters:
#LogFilter.Instance.ListFilters()

#Turn off DEBUG filter (will generate a ton of logs)
#LogFilter.Instance.RemoveFilter(".*", ".*", "DEBUG", True)

#See debug logs from stage (turn _off_ the filters above this level)
#LogFilter.Instance.AddThresholdFilter("svc:/instrument/stage/.*", ".*", LogLevel.DEBUG, False)

#
# Utility functions - move elsewhere eventually
#

#
# Log utils
#

def defaultConsoleLogging():
    #clear any squelches
    LogManager.Instance.ClearAllConsoleSquelch()    
    #Show INFO and above by default
    LogManager.Instance.SetConsoleLevel(LogLevel.INFO)
    #Don't want to see Alarm Clear events 
    LogManager.Instance.SetConsoleSquelch(AlarmLogEvent, LogLevel.INFO)
    #Don't want to see PerfMon's in console...
    LogManager.Instance.SetConsoleSquelch(PerfLogEvent, LogLevel.INFO);


defaultConsoleLogging()

def zipit():
    """ Turn off log output at the Console so you can think straight.  
    Use 'blab()' to see logs at the Console again """
    LogManager.Instance.SetConsoleLevel(LogLevel.CRITICAL)
    
def blab():
    """ Enable logs at the Console again 
    Use 'zipit()' to squelch all Console logging """
    #Note that the LogFilters will typically squelch all logs below info level
    # so we will typically not see TRACE & DEBUG
    LogManager.Instance.SetConsoleLevel(LogLevel.TRACE)
    
def cls():
    """ clear the screen """
    os.system(['clear','cls'][os.name == 'nt'])

def vislog(label, obj):
    """Log a graphical object"""
    global logger
    
    logger.Log(VisualLogEvent(label, obj))
   
def logRawImage(camera, label):
    """ Log a raw image """
    name =  str(camera.Parent.ShortName)
    camera.Snapshot(True)
    ImageLogger.Instance.LogRaw(camera.ImageFrame, label + '_' + name + '_')
   
def logListFilters():
    """List logging filters"""
    LogFilter.Instance.ListFilters()

def RalphBeQuiet():
    lm = LogManager.Instance
    lm.SetConsoleSquelch("svc:/AlarmManagerSvc/")
    lm.SetConsoleSquelch("StageBoard")

#
# Debug utils
#


def dump(obj):
    """Dump a particular C# object properties"""
    from System.Reflection import MemberTypes
    from PacBio.Common.IO import DumpUtil

    DumpUtil.Dump(obj, MemberTypes.Property | MemberTypes.Field)

def methods(obj):
    """Print methods for a particular C# object"""
    from System.Reflection import MemberTypes
    from PacBio.Common.IO import DumpUtil

    DumpUtil.Dump(obj, MemberTypes.Method)

def members(obj):
    """Print property members for an object"""
    from System.Reflection import MemberTypes
    from PacBio.Common.IO import DumpUtil
    DumpUtil.Dump(obj, MemberTypes.Property)

def view(obj):
    """Visualize a particular object if visualization is supported"""
    from PacBio.Common.Diagnostics import VisualizerRegistry
    if not VisualizerRegistry.Instance.Visualize(obj.ToString(), obj, None):
        print "No visualizer registered for this object type or GUI is not enabled..."

def problemDevices():
    dl = instrument.FSM.ProblemDevices
    for d in dl:
        print str(d.FullName) + ", state: " + str(d.CurrentState)

def uninitializedDevices():
    dl = instrument.FSM.UninitializedDevices
    for d in dl:
        print str(d.FullName) + ", state: " + str(d.CurrentState)

from PacBio.Common.Version import *
def swRev():
    print "Version: ", VersionUtils.SoftwareVersion
    print "Revision: ", VersionUtils.SoftwareRevision
    print "BuildDate: ", VersionUtils.SoftwareRevisionDateTime
    try:
        print "Otto: ", instrument.OttoSvcVersion
    except:
        print "Otto missing"

    #eventually this will have more info (bug 5682)
    for rtBoard in instrument.RTBoards:
        print "\nRT Board: ", rtBoard.Key
        print "   ", rtBoard.Value
    
   
#
# Camera utils
#

def setLUT(cam, low = 0, range = 256):
    "Set the LUT for one of the Otto cameras"
    cam.SetCustomIndexTable(low, range)
    cam.Snapshot(True)

def setLUTs(low = 0, range = 256):
    "Set the LUTs for all 4 cameras"
    cam1.SetCustomIndexTable(low, range)          
    cam2.SetCustomIndexTable(low, range)          
    cam3.SetCustomIndexTable(low, range)          
    cam4.SetCustomIndexTable(low, range)
    cam1.Snapshot(True)
    cam2.Snapshot(True)
    cam3.Snapshot(True)
    cam4.Snapshot(True)      
    
#setup camera for viewing
# can use a camera 
def viewCam(camera, exposure=0.1, interval=0.5):
	camera.Exposure = exposure
	camera.PollInterval = interval
	view(camera)

def viewAll():
	viewCam(cam1)
	viewCam(cam2)
	viewCam(cam3)
	viewCam(cam4)
	
def fscore(frameOrCam):
	try:
		return FrameUtils.BrennerFocusScore(frameOrCam)
	except:
		return FrameUtils.BrennerFocusScore(frameOrCam.Snapshot(True))
	
def sleep(mils):
	from System.Threading import *
	Thread.Sleep(mils)

# this is a workaround for WaitForMove not working		
# times are in millisec
def fakeWait(axis, epsilon=5e-6, timeout=30000, sleepTime=100):
	maxTries = timeout/sleepTime # 30-second timeout if you sleep 10 ms
	tries = 0
	while (abs(axis.TargetPosition - axis.CurrentPosition) > epsilon) and (tries < maxTries):
		sleep(sleepTime)
		tries = tries + 1
		print axis.TargetPosition, axis.CurrentPosition, axis.TargetPosition-axis.CurrentPosition
	if tries >= maxTries:
		print "fakeWait timed out"
			         
#
# Simulate instrument startup/shutdown operations eventually submitted via Quimby
#

def shutdown():
    """Shutdown the instrument"""
    global instrument
    instrument.FSM.SkipPausedShutdown=True
    instrument.FSM.Shutdown(False)	# graceful shutdown request

def Shutdown():
    shutdown()

#
# Provide an easy command to quit homer without causing a power down if the
# instrument has power control. And also the opposite, to force a power down
#

def quithomer():
    """Quit homer"""
    global instrument
    print 'Quitting Homer'
    instrument.FSM.QuitHomer()

def Quithomer():
    quithomer()

def QuitHomer():
    quithomer()

def quitHomer():
    quithomer()

def powerdown():
    """Power down instrument"""
    global instrument
    print 'Powering down'
    instrument.FSM.PowerDown()

def PowerDown():
    powerdown()

def powerDown():
    powerdown()

def Powerdown():
    powerdown()

#
# Alarm squelching
#

def SquelchAlarm(name, reason):
    instrument.AlarmManagerSvc.AddAlarmSquelch("*", name, reason)

def squelchAlarm(name, reason):
    SquelchAlarm(name, reason)

def ClearSquelch(name):
    instrument.AlarmManagerSvc.RemoveAlarmSquelches("*", name)

def clearSquelch(name):
    ClearSquelch(name)

def removeSquelch(name):
    ClearSquelch(name)

def RemoveSquelch(name):
    ClearSquelch(name)

#
# Support Mode shortcuts
#

def beginsupportmode(description):
    instrument.BeginSupport(description)

def BeginSupportMode(description):
    beginsupportmode(description)

def BeginSupportmode(description):
    beginsupportmode(description)

def Beginsupportmode(description):
    beginsupportmode(description)

def BeginSupport(description):
    beginsupportmode(description)

def Beginsupport(description):
    beginsupportmode(description)

def beginsupport(description):
    beginsupportmode(description)

def endsupportmode():
    instrument.EndSupport()

def EndSupportMode():
    endsupportmode()

def EndSupportmode():
    endsupportmode()

def Endsupportmode():
    endsupportmode()

def EndSupport():
    endsupportmode()

def Endsupport():
    endsupportmode()

def endsupport():
    endsupportmode()

def InSupportMode():
    if instrument.InSupportMode:
        print "True"
    else:
        print "False"

def InSupportmode():
    InSupportMode()

def Insupportmode():
    InSupportMode()

def insupportmode():
    InSupportMode()

#
# RT tools
#

def dumpRT():
    """Print info about the RT boards installed in system"""
    for v in instrument.RTBoards.Values:
        print v


def setRTLoad(serveraddr, developername):
    """Set the RT load"""
    print "Setting RT server = ", serveraddr
    print "Setting RT developer = ", developername
    
    for v in instrument.RTBoards.Values:
        print v.SetDeveloperLoad(serveraddr, "rt", developername)                                 

                                  
def rebootRT():
    """Reboot the RT boards"""
    print "Rebooting all RTs... You should exit homer..."
    
    for v in instrument.RTBoards.Values:
        print v.Reboot()
   
   
# Newport Piezo axis control comm stuff
try:
    newport = instrument.IlluminationPath[532].BeamSteeringMirrors.LowLevelVectorAxis
except:
    logger.Log(InstrumentLogEvent("Newport not found"))

    
def np(cmd):
    cmd = cmd.ToUpper()
    # Fix long if statement once I learn how to continue on another line - mewan
    if cmd.Contains("?") or cmd.Contains("MA") or cmd.Contains("PH") or cmd.Contains("TE") or cmd.Contains("TP") or cmd.Contains("TS") or cmd.Contains("VE"):
        return newport.SendCommand(cmd)
    else:
        newport.SendCommandNoResponse(cmd)
        return ""

def axisTest(dev, testNum = 0, min = -4000, max = -1000, step = 100 ):
	"""Do a bunch of moves and check for error accumulation, args in microns"""
	from PacBio.Common.Utils import AssociativeArray
	arr = AssociativeArray()
	for i in range(min, max, step):
		pos = i * 1e-6
		dev.TargetPosition = pos
		dev.WaitForMove()
		print "t=", dev.TargetPosition, " c=", dev.CurrentPosition
		arr[str(i),"TestNum"] = testNum      
		arr[str(i),"Target"] = dev.TargetPosition
		arr[str(i),"Current"] = dev.CurrentPosition
	fname = "testfile-" + str(testNum) + ".csv"
	print "Writing CSV as ", fname
	arr.WriteCSV(fname)

def jamTest(dev, testNum = 0):
    """Walk an axis across full range of travel"""
    # Convert to ints
    min = int(dev.MinPosition / 1e-6)
    max = int(dev.MaxPosition / 1e-6)
    step = (max - min) / 20
    axisTest(dev, testNum, min, max, step)


def swaDoeTest():
    global swa2, doe2
    swa = swa2.VectorAxis
    doe = VectorAxisWrapper(doe2.VectorAxis) # DOE only has one axis so easier
    for i in range(0, 10):
        swapos = \
            ( swa.MinPosition[0] + (swa.MaxPosition[0] - swa.MinPosition[0]) * i * 0.1, \
            swa.MinPosition[1] + (swa.MaxPosition[1] - swa.MinPosition[1]) * i * 0.1)
        doepos = doe.MinPosition + (doe.MaxPosition - doe.MinPosition) * i * 0.1

        # if I move SWA first the problem does not occur
        print "DOE move to", doepos
        doe.BeginMove(MoveType.Absolute, doepos)

        print "SWA move to", swapos
        swa.BeginMove(MoveType.Absolute, swapos)

        print "DOE wait for move"
        MovementException.Check(doe.WaitForMove())

        print "SWA wait for move"
        MovementException.Check(swa.WaitForMove())

def doeTest():
    global doe2
    doe = VectorAxisWrapper(doe2.VectorAxis) # DOE only has one axis so easier
    for i in range(0, 10):
        doepos = doe.MinPosition + (doe.MaxPosition - doe.MinPosition) * i * 0.1
        print "DOE move to", doepos
        doe.BeginMove(MoveType.Absolute, doepos)

        print "DOE wait for move"
        MovementException.Check(doe.WaitForMove())

def swaTest():
    global swa2
    swa = swa2.VectorAxis
    for i in range(0, 10):
        swapos = \
            ( swa.MinPosition[0] + (swa.MaxPosition[0] - swa.MinPosition[0]) * i * 0.1, \
            swa.MinPosition[1] + (swa.MaxPosition[1] - swa.MinPosition[1]) * i * 0.1)
        print "SWA move to", swapos
        swa.BeginMove(MoveType.Absolute, swapos)

        print "SWA wait for move"
        MovementException.Check(swa.WaitForMove())

def doStress(funct):
    """Do a bunch of moves and check for error accumulation"""
    for numtries in range(1, 100):
        funct()


def axisStress(dev):
    """Do a bunch of moves and check for error accumulation"""
    for numtries in range(1, 100):
        jamTest(dev, numtries)

# calRalph/calNelson etc... moved to calibration.py
        
#
# View illumination path controls
#

def viewIllumPath(wavelength):
    path = instrument.IlluminationPath[wavelength]
    view(path.BeamSteeringMirrors)
    view(path.BeamExpander)
    view(VOAPSB(path.VOA, path.PSB))
    view(path.SWA)
    view(path.DOE)
    view(path.RelayLensGroup)

def viewGrn():
    viewIllumPath(532)

def viewRed():
    viewIllumPath(642)

#
# Chip clamp
#

def clampOpen():
	clamp.SetState(ChipClampState.ReadyForUnload)

def clampClose():
	clamp.SetState(ChipClampState.Clamped)

def tdOpen():
    """Open Trap Door"""
    td.BeginOpen(True)
    td.EndMove()
    
def tdClose():
    """Close Trap Door"""
    td.BeginOpen(False)
    td.EndMove()

#
# movie taking
#

def captureMovie(filename = "testmovie.mov.h5", numFrames = 100, stride = 0):
    """Grab a movie with otto, default to one minute (if exposure is 10 ms), with no skipped frames"""
    gui = instrument.CameraSet.Subframe(SubframeID.GUI_PREVIEW_SUBFRAME)
    ms = instrument.CameraSet.Subframe(SubframeID.MOVIE_THUMBNAIL_SUBFRAME)
    ms.GrabRect = gui.GrabRect
    ms.Enabled = True
    instrument.CameraSet.StartMovieCapture(filename, numFrames, stride)
    
#
# swat temperature debugging
#

def swatLog(cameras=[bsbrCam, cam1, cam2, cam3, cam4], numFrames=60, frameInterval=60):
    """Log cam frames """
    basename="swatlog-" + time.strftime("%H-%m-%S")

    mlog = MovieLogger(basename, len(cameras))
    from PacBio.Common.Utils import AssociativeArray
    arr = AssociativeArray()

    for i in range(0, numFrames):
        print "Taking frame", i
        arr[str(i),"FrameNum"] = i   
        camNum = 0
        for cam in cameras:
            f = cam.Snapshot(True)
            mlog.Log(camNum, f)
            camNum = camNum + 1
               
        arr[str(i),"mpbLDTemp"] = mpb.LDTempC
        arr[str(i),"mpbTECTemp"] = mpb.TECTempC
        arr[str(i),"coherentLDTemp"] = coherent.LDTempC
        arr[str(i),"coherentTECTemp"] = coherent.TECTempC
        sleep(frameInterval)
        
    mlog.Dispose()
    fname = basename + ".csv"
    print "Writing CSV as ", fname
    arr.WriteCSV(fname)

#
# Capture # frames from all cameras
# to h5 movie fle 
# @param name - file name prefix. if starts with "/" then specifies full path.
#

def capture(name="", frames=1, cameras=[bsbrCam, cam1, cam2, cam3, cam4]):
    if name == "":
       name = "capture";
    basename = name + "-" + time.strftime("%H-%m-%S");

    mlog = MovieLogger(basename, len(cameras))
	
    print("Capture %d frame(s) to [%s]" % (frames, mlog.Filepath));

    for i in range(0, frames):
        print("Taking frame %d" % i);
        camNum = 0
        for cam in cameras:
            f = cam.Snapshot(True)
            print("   from camera: %s" % cam.ToString());
            mlog.Log(camNum, f)
            camNum = camNum + 1
        
    mlog.Dispose()
    print("Done\n");

#
# Memory debugging
#

def dumpHeap():
    """Dump heap information"""
    HeapCounter.DumpAll()
    MemoryPool[System.UInt16].Instance.Dump()
    MemoryPool[System.Byte].Instance.Dump()
    MallocUtils.malloc_stats()

# 
# Thread debugging
#

def dumpThreads():
    """List all running managed threads"""
    ThreadRegistry.Dump(System.Console.Out)
    
def dumpStacks():
    """Dump stack traces for all managed threads"""
    ThreadRegistry.DumpStacks(System.Console.Out)
    

#
# Show me the inventory of the drawers
#

def PrintPlateInfo(name, plate):
	print "   ",name,
	if (plate.PresenceState == PlatePresenceState.Present):
		print " present ", plate.Barcode,
		if (plate.BarcodeError == "Expired"):
			print " EXPIRED",
		if (not plate.HasRealBarcode):
			print " (manually set)."
	else:
		print " absent"

def ShowInventory():
	rl = instrument.TemplateReagentDrawer
	ct = instrument.ChipsTipsDrawer
	print "Inventory:"
	PrintPlateInfo("Sample Plate", rl.TemplateReagentTray.TemplatePlate)
	PrintPlateInfo("Reagent Plate 0", rl.TemplateReagentTray.ReagentKitPlate0)
	PrintPlateInfo("Reagent Plate 1", rl.TemplateReagentTray.ReagentKitPlate1)
	PrintPlateInfo("Reagent Tube 0_0", rl.TemplateReagentTray.ReagentTube0_0)
	PrintPlateInfo("Reagent Tube 0_1", rl.TemplateReagentTray.ReagentTube0_1)
	PrintPlateInfo("Reagent Tube 1_0", rl.TemplateReagentTray.ReagentTube1_0)
	PrintPlateInfo("Reagent Tube 1_1", rl.TemplateReagentTray.ReagentTube1_1)
	# mixing plate lacks a barcode, just show presence
	mixing = rl.TemplateReagentTray.MixingPlate
	if (mixing.PresenceState == PlatePresenceState.Present):
		print "    Mixing Plate  present"
	else:
		print "    Mixing Plate  absent"
	# now tips and chips
	chips = ct.ChipTray
	strips = chips.ChipStripCount
	totalchips = chips.ChipCount
	print "    Chip strips ",strips," with ",totalchips," chips and barcodes:"
	index= 0
	while (index< chips.ChipStripCapacity ):
		strip = chips.GetChipStrip(index)
		PrintPlateInfo("    ["+str(index)+"] ", strip)
		index= index+ 1
	tips = ct.PipetteTipTray
	boxcount = tips.BoxCount
	boxcap = tips.BoxCapacity
	tipcount = tips.TipCount
	print "    Tip boxes ",boxcount," with ",tipcount ," total tips:"
	index= 0
	while (index< boxcap ):
		box = tips.GetTipBox(index)
		print "    [",str(index),"] ",
		if (box.IsCovered):
		    print "present  covered"
		elif (box.PresenceState == PlatePresenceState.Present):
			print "present ",box.TipCount
		else:
			print "absent"
		index= index+ 1
	vt = instrument.Robot.VisionTools
	if (vt.Fiducials.ContainsKey("SWATJig")):
		print "    TestJig: "+chips.TestJig.PresenceState.ToString()+"  "+chips.TestJig.Barcode
		for j in range(0,6):
			print "      Station "+str(j)+"  "+chips.TestJig.AllTestJigStations[j].ChipOccupied.ToString()


#
# Primary analysis protocol testing
#

from PacBio.Instrument.Analysis.Pipeline import *

def testCluster():
    """A basic test that feeds a canned small tracefile into sideshowbob"""
    Cluster.TestInvoke()
    
#
# Protocol testing
# temporily here for testing the swat protocol
#

from protocols import *

def testProto():
    """Limit us to one frame for speed"""
    RunProtocol("SquatMovieOnlyProtocol.py", AcquisitionTime=0.010)

def runProtoOneMinuteCustomTI():
    """An example of how to customize parameters"""
    RunProtocol("SquatMovieOnlyProtocol.py", AcquisitionTime=TimeSpan(0,0,60), TILevel2=0.50, Filename='IHateCats')    
        
def runProto():
    RunProtocol("SqwatAcquisitionProtocol.py")

def runProtoMovieOnly():
    RunProtocol("SquatMovieOnlyProtocol.py")

def abortProto():
    instrument.Acquisition.BeginAbort()
    instrument.ChipAlignment2.BeginAbort()
    
def wflog(fp, msg):
    ts = time.strftime("%c")
    outputString =  "[" + ts + "] " + msg
    print outputString
    if fp != 0:
        fp.write(outputString + "\n")


def runAligner():
    leakcheck = HalconDBSnapshot()
    print "Prepare alignment..."
    cas2.PrepareChipAlignment()
    
    print "Performing alignment..."
    cas2.AlignChip("fish", 1, ChipAlignmentKind.FullAlignment)
    leakcheck.CheckLeaks()
    print "Done with test"

def stressAligner():
    t = 0.5
    cam1.PollInterval = t
    cam2.PollInterval = t
    cam3.PollInterval = t
    cam4.PollInterval = t
    bsbrCam.PollInterval = t
    clampOpen()
    clampClose()
    for i in range(1, 1000):
        GC.Collect()
        GC.WaitForPendingFinalizers
        HeapCounter.DumpAll()
        print "*** Stress #", i, " mem=", GC.GetTotalMemory(False)
        #r.Scan()
        runAligner()

def stressRobot():
    for i in range(1, 1000):
        r.Scan()

def heapStress():
    """look for bug 10206"""
    ThreadUtils.Start(stressRobot, "robotstress")
    stressAligner()


def XYZWorkflow(outputDirectory="",enableZMotion=False):
    """
    XYZWorkflow executes a representative workflow motion for the
    purpose of evaluating effects of XYZ robot motion on other 
    modules in the system
    """

    shouldOutputToFile = True    
    if (outputDirectory == ""):
        shouldOutputToFile = False

    outputFp = 0

    if (shouldOutputToFile == True):
        # Check if directory exists
        if os.path.isdir(outputDirectory) == False:
            try:
                os.mkdir(outputDirectory)
            except Exception, e:
                print "Error creating output directory: " + outputDirectory
                print repr(e)

        # Just as a sanity check, make sure the output directory is there
        if os.path.isdir(outputDirectory) == False:
            raise Exception("Output directory does not exist: " + outputDirectory)

        # Find appropriate output filename
        baseOutputFilename = "workflow"
        fileIndex = 1

        while os.path.isfile(os.path.join(outputDirectory,baseOutputFilename + str(fileIndex) + ".txt")):
            fileIndex = fileIndex + 1

        outputFilename = os.path.join(outputDirectory,baseOutputFilename + str(fileIndex) + ".txt")

        outputFp = open(outputFilename, 'w')

    r = InstrumentContext.Instrument.Robot
    rc = r.RControl
    z = rc.ZAxes
    xy = rc.XYAxes

    print "-----------------------------------------------"
    print "Homing XYZ"
    print "-----------------------------------------------"
    rc.XInitAxes()

    print "-----------------------------------------------"
    print "Starting sample workflow motions"
    print "Hit Ctrl-C to stop"
    print "enableZMotion is: "+str(enableZMotion)
    if shouldOutputToFile:
        print "Motions logged at: " + outputFilename
    print "-----------------------------------------------"

    NO_DESCEND, SHALLOW_DESCEND, DEEP_DESCEND = range(3)
    Z_SHALLOW_DESCEND = 0.09
    Z_DEEP_DESCEND = 0.18

    # Locations stored as X, Y, Z
    
    locations = ((0.017,-0.063,SHALLOW_DESCEND),
                 (-0.134, 0.130, NO_DESCEND),
                 (0.042,0.096,SHALLOW_DESCEND),
                 (-0.788,-0.145, NO_DESCEND))
    """
    locations = ((0.017,-0.063,SHALLOW_DESCEND),
                 (-0.134, 0.130, NO_DESCEND),
                 (0.042,0.096,SHALLOW_DESCEND))  
    """

    numLocations = len(locations)

    iMove = 1
    iCycle = 0

    xy.Controller.DrivesOn()

    try:
        while True:
            wflog(outputFp, "Start move " + str(iMove) + ": " + "Raise Z Axis")
            rc.RaiseZ()
            wflog(outputFp, "End move " + str(iMove) + ": " + "Raise Z Axis")
            iMove = iMove + 1

            # Go to various locations
            locationIndex = iCycle % numLocations
            iCycle = iCycle + 1
            
            currentXY = xy.CurrentPosition
            x = locations[locationIndex][0]
            y = locations[locationIndex][1]
            wflog(outputFp, "Start move " + str(iMove) + ": " + "XY: from (" + str(currentXY[0]) + "," + str(currentXY[1]) + ")" + " to (" + str(x) + "," + str(y) + ")")
            xy.TargetPosition = (x,y)
            xy.WaitForMove()
            wflog(outputFp, "End move " + str(iMove) + ": " + "XY: from (" + str(currentXY[0]) + "," + str(currentXY[1]) + ")" + " to (" + str(x) + "," + str(y) + ")")
            iMove = iMove + 1

            # XY could have failed.  Verify position before lowering Z
            currentXY = xy.CurrentPosition
            if ((abs(currentXY[0] - x) > 0.003) or (abs(currentXY[1] - y) > 0.003)):
                raise Exception("XY didn't converge to target position")

            zTargetPosition = z.CurrentPosition
            zTargetDescription = "no descend"
            
            if (enableZMotion==True):
                if (locations[locationIndex][2] == SHALLOW_DESCEND):
                    zTargetPosition[2] = zTargetPosition[2] + Z_SHALLOW_DESCEND
                    zTargetDescription = "shallow descend"
                elif (locations[locationIndex][2] == DEEP_DESCEND):
                    zTargetPosition[2] = zTargetPosition[2] + Z_DEEP_DESCEND
                    zTargetDescription = "deep descend"
	         
                if locations[locationIndex][2] != NO_DESCEND:
                    wflog(outputFp, "Start move " + str(iMove) + ": " + "Lowering Z Axis: " + zTargetDescription)
                    z.TargetPosition = zTargetPosition
                    wflog(outputFp, "End move " + str(iMove) + ": " + "Lowering Z Axis: " + zTargetDescription)
                    z.WaitForMove()
                    iMove = iMove + 1

            time.sleep(1)

    except KeyboardInterrupt:
            print "User cancelled motions."
    except System.Exception, e:
            print "Error: " + repr(e)       

    z.WaitForMove()
    rc.RaiseZ()

    print "-----------------------------------------------\n"
    print "Stopping XYZ workflow motions."
    if shouldOutputToFile:
        print "Motions logged at: " + outputFilename
        outputFp.close()

def LogParkerDriveTemperature(outputDirectory=""):
    """
    LogParkerDriveTemperature queries the temperature of the Aries drives.
    """

    shouldOutputToFile = True    
    if (outputDirectory == ""):
        shouldOutputToFile = False

    outputFp = 0

    if (shouldOutputToFile == True):
        # Check if directory exists
        if os.path.isdir(outputDirectory) == False:
            try:
                os.mkdir(outputDirectory)
            except Exception, e:
                print "Error creating output directory: " + outputDirectory
                print repr(e)

        # Just as a sanity check, make sure the output directory is there
        if os.path.isdir(outputDirectory) == False:
            raise Exception("Output directory does not exist: " + outputDirectory)

        # Find appropriate output filename
        baseOutputFilename = "drive_temperature"
        fileIndex = 1

        while os.path.isfile(os.path.join(outputDirectory,baseOutputFilename + str(fileIndex) + ".txt")):
            fileIndex = fileIndex + 1

        outputFilename = os.path.join(outputDirectory,baseOutputFilename + str(fileIndex) + ".txt")

        outputFp = open(outputFilename, 'w')

    r = InstrumentContext.Instrument.Robot
    rc = r.RControl
    z = rc.ZAxes
    xy = rc.XYAxes
    controller = xy.Controller
    
    if shouldOutputToFile:
        print "Temperatures logged at: " + outputFilename
    print "-----------------------------------------------"

    try:
        while True:
            driveTemperature = controller.DriveTemperature
            wflog(outputFp, "X drive temperature " + str(driveTemperature[0]) + " degrees Celsius")
            wflog(outputFp, "Y drive temperature " + str(driveTemperature[1]) + " degrees Celsius")
            
            time.sleep(10)

    except KeyboardInterrupt:
            print "User cancelled temperature logging."
    except System.Exception, e:
            print "Error: " + repr(e)       

    print "-----------------------------------------------\n"
    print "Stopping drive temperature logging."
    if shouldOutputToFile:
        print "Temperatures logged at: " + outputFilename
        outputFp.close()
        
#
# Tools for protocol debugging
#

from PacBio.Common.Scheduler import *
from PacBio.Instrument.Protocols import *

def pSS():
    """Turn on single stepping for protocols"""
    print "FIXME - deprecated - will not work - Single stepping on..."
    ScheduleRunner.SingleStep = True

def pSOff():
    """Turn off single stepping for protocols"""
    print "FIXME - deprecated - will not work - Single stepping off..."
    ScheduleRunner.SingleStep = False

def pS():
    """FIXME - deprecated - will not work - Step over next protocol entry (when at a breakpoint)"""
    ScheduleRunner.Instance.Continue()

def pGoto(entryNum):
    """FIXME - deprecated - will not work - Go to a particular protocol step # (use with care)"""
    ScheduleRunner.Instance.SetNext(entryNum)

def allowEarlyStarts(allow = True):
    """FIXME - deprecated - will not work - If true we will skip all scheduler driven sleeps (for testing/sim purposes)"""
    ScheduleRunner.AllowEarlyStarts = allow
    ProtocolLiquidToolKit.RealPauses = not allow

from simtools import *

def MakeSimTools():
    return SimToolsFake()

#these scanners depend on the vision includes
#these will not be right if the reagent loader gets excluded     
#if instrument.Robot.InventoryScanner != None:
#    chipScanner = instrument.Robot.InventoryScanner.Scanners[1]
#    reagentScanner = instrument.Robot.InventoryScanner.Scanners[0]
rdrawer = instrument.TemplateReagentDrawer
cdrawer = instrument.ChipsTipsDrawer


# draw homer, because we can
drawHomer = DrawHomer()
drawHomer.Draw()

# Display DB check error message
Program.DisplayDBCheckError()

#
# Load user specific settings 
#

def GetUserScriptName():
    script = None
    try:
        script = os.path.join(Program.ScriptsDir, os.environ["USERNAME"] + "-startup.py")
    except:
        pass
    if script is None:
        try:
            script = os.path.join(Program.ScriptsDir, os.environ["USER"] + "-startup.py")
        except:
            pass

    if script != None and os.path.exists(script):
        return script
    else:
        return None

im = instrument.InterlockManager # convenience shortcut for interlock manager

userScript = GetUserScriptName()
if userScript != None:
    if (instrument.StringHash.Add(userScript)):
        logger.Log(ProgramLogEvent("Loading user startup script " + userScript))
        execfile(userScript)
    else:
        print "Skipping '" + userScript + "'; already loaded on some other console. execfile() manually if you like."


#
# Assembly debugging
#

def ListAssemblies():
    list = AppDomain.GetAssemblies(AppDomain.CurrentDomain)
    for assembly in list:
        try:
            print " ",assembly.GetName().Name.ljust(30)," ",assembly.Location
        except:
            pass
