#
# kevin's standard homer debug environmnet
#

import clr

from PacBio.Instrument.Axis import SimVectorAxis

from PacBio.Instrument.Stage import *

from PacBio.Instrument.RT import *
from PacBio.Instrument.Devices import *
from PacBio.Instrument.Interfaces.Movement import *
from PacBio.Instrument.Interfaces import *
from PacBio.Common.Movie import *
from PacBio.Instrument.BSBR import * 
from PacBio.Instrument.BSBR.Test import * 
    
clr.AddReference('PacBio.Common.Numeric')
clr.AddReference('PacBio.Instrument.Axis')
clr.AddReference("PacBio.Instrument.Alignment")  
clr.AddReference('PacBio.Instrument.Interfaces.Movement')
clr.AddReference('PacBio.Instrument.RT')
clr.AddReference('PacBio.Instrument.Chip')
clr.AddReference('PacBio.Instrument.Stage')

from System import *
from PacBio.Common.Numeric import *
from PacBio.Common.Utils import *
from PacBio.Common.Frames import *
from PacBio.Instrument.Axis import *
from PacBio.Instrument.Interfaces.Movement import *
from PacBio.Instrument.RT import *
from PacBio.Instrument.Stage import *
from PacBio.Instrument.Homer import *
from PacBio.Instrument.Chip import *
from PacBio.Instrument.Alignment import *
from PacBio.Instrument.Alignment.Test import *
from System import *
from System.Collections import *
from System.Collections.Generic import *
from System.Drawing import *
from PacBio.Instrument.Camera import *
from PacBio.Instrument.Alignment import *
from PacBio.Instrument.Halcon import *

# g = RTBoard.Get(IGPIO, "10.10.5.155", "/gpio")
# clamp.SetState(ChipClampState.ReadyForLoad)

camera = instrument.CollectionPath[633].Camera

def InitTEC():
    global clamp
    loop = clamp.TempControl.Ctrl
    loop.SetOMax(0, 900)
    loop.SetOMin(0, -900)
    loop.SetKc(0, 1)

    loop.SetSetpoint(0, 22)
    
    # loop.SetEnable(0, True)

def startcam():
    camera.StartPreviewImaging()
    
def camSingleThread(val):
    global instrument
    instrument.CollectionPath[433].Camera.SingleThreaded = val
    instrument.CollectionPath[488].Camera.SingleThreaded = val
    instrument.CollectionPath[538].Camera.SingleThreaded = val
    instrument.CollectionPath[633].Camera.SingleThreaded = val
    
def camBlurSingleThread(val):
    global instrument
    instrument.CollectionPath[433].Camera.BlurSingleThreaded = val
    instrument.CollectionPath[488].Camera.BlurSingleThreaded = val
    instrument.CollectionPath[538].Camera.BlurSingleThreaded = val
    instrument.CollectionPath[633].Camera.BlurSingleThreaded = val
    
def testHovig():
    global sl
    
    qdc = QuickAndDirtyDataCameraSimulator("S:\\Software\\HovigTest\\layout\\chiplayout.xml.gz", instrument, 2584, 2160)

    focalROI = ROIUtil.RectangularGrid(20, 20, qdc.GrabRect)
    rfm = RegionFocalMeasure(focalROI)
    stackTrajectory = TrajectoryUtil.LinearTrajectory((0, 0, -50e-6, 0, 0, 0), (0, 0, 50e-6, 0, 0, 0), 20)

    sl = StageLeveler(qdc, instrument.Stage)
    

qdc = None

def stressQDC():
    global qdc
    
    qdc = QuickAndDirtyDataCameraSimulator("S:\\Software\\HovigTest\\layout\\chiplayout.xml.gz", instrument, 2584, 2160)

    for i in range(0,100):
        print "trying " + str(i)
        vislog("qdc-stress", qdc.Snapshot(True))

def testQDC():
    global qdc
    
    if qdc is None:
        qdc = QuickAndDirtyDataCameraSimulator("S:\\Software\\HovigTest\\layout\\chiplayout.xml.gz", instrument, 2584, 2160)
    
    td = TestDummy()
    td.TestStageLeveler(qdc)


def testDon():
    td = TestDummy()
    td.TryFail(cam1.Snapshot(True), cam2.Snapshot(True))


def testLevel():
    t = TestChipLeveler()
    t.testChipLeveler()
    
def asyncLevel():
    global instrument
    
    s = instrument.ChipLevelerSvc
    return s.BeginLevelChip()
    
def testBlur():
    global instrument
    
    t = TestSimBlurring()
    t.TestBlur(instrument) 
    
def stageFindIndex():
    global stage
    stage.FindIndex()

def testPlot():
    p = SimplePlot()
    p.TestMultiplot()
    
def testImage():
    global instrument
    view(instrument.CollectionPath[538].Camera.Snapshot(True))

def testTransform():
    TransformStack.TestTranslation()
    ProjectiveTransform2D.TestInvert()
    TransformStack.Test()
    
camera = instrument.CollectionPath[538].Camera
robotIllum = instrument.Robot.ZIlluminator

# browse the stuff I usually care about
#browse(coherent)
#browse(mpb)
#browse(stage)
#browse(camera)
 
#import clr
#clr.AddReference("PacBio.Common.Chunk.HDF")
#from PacBio.Common.Chunk.HDF import *

# testPlot()

# clr.AddReference("PacBio.Common.Chunk.HDF")
# from PacBio.Common.Chunk.HDF.Test import *
#
#def TestHDF():
#    t = HDFTest()
#    t.TestAttributeWrite()

# testBlur()
# testLevel()
# testQDC()
# testTransform()


def test2():
    t = instrument.CollectionPath[538].StageToCameraPath
    print t.FocalPlaneMetersToCameraPixels(1e-6, 1e-6)

# test2()

#v = instrument.IlluminationPath[532].VOA
#browse(v)
#browse(v.Axis)
#a = v.Axis
#a.Enabled = True

#psb = instrument.IlluminationPath[532].PSB
#browse(psb)

#browse(RTBoard.GetProxies())

# a.FindIndex()

# The following should fail
# a.TargetPosition = a.MaxPosition
# print a.WaitForMove()

# dumpToFile()

# stage.FindIndex()

# f = camera.Snapshot(True)
# dump(f)
# view(camera)

z = VectorAxisWrapper(stage.Axis, 2)
# view(z)

def moveZ(dest):
    print "Setting Z", dest
    z.TargetPosition = dest
    MovementException.Check(z.WaitForMove())

def testZ(z):
    for i in range(-4, 4):
        moveZ(z + i * 100e-6)
    
def stressZ():
    stage.AutoAxis = True
    stage.Axis.FindIndex()
    MovementException.Check(stage.Axis.WaitForMove())
    zv = 0
    for i in range(1, 100):
        testZ(zv) 

def oldViewCam():
    # Init the stage
    stage.Axis.FindIndex()
    
    illum.Brightness = 0.3
    illum.Enabled = True
        
    # camera.GrabRect = Rectangle(0, 0, 512, 512) # For preview speed
    camera.Exposure = 0.1
    camera.PollInterval = 1 # seconds
    camera.StartPreviewImaging()
    view(camera)
    z.TargetPosition = 140e-6   # A good initial Z
    
def testHovig2():
    from PacBio.Instrument.Alignment import *
    f = camera.Snapshot(True)
    ImageLogger.Instance.Log("foo", f)

# stage.Axis.FindIndex()

illum = instrument.Illuminator
# illum1 = illum.Target.Channels[0].Illuminator

def testSteer():
    alignment = fineSteer
    alignment.DesiredState = BeamSteerState.Steering
    alignment.WaitForState(BeamSteerState.Steering);
    alignment.DesiredState = BeamSteerState.Idle;
    alignment.WaitForState(BeamSteerState.Idle);            


# clr.AddReference("PacBio.Intrument.BSBR")


def testBSBR():
    global bm
    MOVIE_FILENAME = "C:\\temp\\Stage_Theta-stack_0p5mrad_10-15-09.moviestack.mov.h5"
    bm = BSBRMeasurement(bsbrCam) 
    bm.FitRegions = (BSBRRegion.HighlandRed, BSBRRegion.LowlandRed, BSBRRegion.HighlandGreen,BSBRRegion.LowlandGreen)
    md = MovieDocument(MOVIE_FILENAME)
    frame = md.GetFrame(0)
    #bm.Register(frame)
    #bm.Register(frame)
    #bm.Measure(frame)


def testMovieWriting():
    instrument.CameraSet.TestMovieWriting()

def testCrude():
    instrument.BSBR.CameraSet.CrudeMovieCapture("test", 30, 30, -1) 

   
def testBSBRWriting():
    instrument.BSBR.CameraSet.TestMovieWriting()

def testUk():
    from PacBio.Instrument.Alignment.Test import *
    TestuKels().testuKELS()

def convertUk():
    from PacBio.Instrument.Alignment.Test import *
    TestuKels().convertFiles()


md = None
bm = None
roi = None

# the following runs all day just fine
def bsbrMemory():
    global md
    global bm
    global roi
    
    if md == None:
        MOVIE_FILENAME = "C:\\temp\\Stage_Theta-stack_0p5mrad_10-15-09.moviestack.mov.h5"
        md = MovieDocument(MOVIE_FILENAME)
        
    testframe = md.GetFrame(0)
    print "got frame"
        
    if roi == None:
        chipLayoutSvc = ChipLayoutSvcBasic()
        chipLayoutProvider = chipLayoutSvc.GetChipLayout("NC1L120", 1)
        roi = BSBRROIGenerator(chipLayoutProvider, bsbrCam.ImagePlaneToCameraPixels)
        
    if bm == None:
        bm = BSBRMeasurement(roi)
        fitRegions = ( BSBRRegion.HighlandRed, BSBRRegion.LowlandRed , BSBRRegion.HighlandGreen, BSBRRegion.LowlandGreen )
        bm.Initialize(testframe, fitRegions)
        
    print "running loop"    
    for i in range(0, 10):
        testframe = md.GetFrame(i)
        bm.Measure(testframe)
        GC.Collect();
        GC.WaitForPendingFinalizers()
        print "Total mem", GC.GetTotalMemory(False)
        HeapCounter.DumpAll()
       

def camMemory():
    for i in range(0, 50):
        f = bsbrCam.Snapshot(True)
        # GC.Collect();
        # GC.WaitForPendingFinalizers()
        print GC.GetTotalMemory(False)
        HeapCounter.DumpAll()       

def testAndy():
    """Andys BSBR test case"""
    ti.Enabled = True
    ti.Target.Enabled = True
    ti.Target.Brightness = 1.0
    PacBio.Instrument.BSBR.Test.TestBSBR().testBSBRMeasurement()





# drttemp = RTBoard.Get(IVectorEncoder, instrument.IECBoard, "/drt-0/temperature")



# testBSBRWriting()

# runProto()

# use strips now and don't wait for immob
#allowEarlyStarts()
cdrawer.ChipTray.IsAvoidJig = True
# r.PickupPlaceChip.PlaceChipDropHeight = -0.001

def debugMachines():
    from PacBio.Common.Services import *
    d = StateMachineDebugger()
    CommonStateMachine.AddGlobalHook(d)
    
# debugMachines()

instrument.FSM.SkipStabilization=True
allowEarlyStarts()
