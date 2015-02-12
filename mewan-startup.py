#
# mark ewan's standard homer debug environmnet
#

import clr

from PacBio.Instrument.Axis import SimVectorAxis

from PacBio.Instrument.Stage import *

from PacBio.Instrument.RT import *
from PacBio.Instrument.Devices import *
from PacBio.Instrument.Interfaces.Movement import *
from PacBio.Instrument.Interfaces import *
 
clr.AddReference('PacBio.Common.Numeric')
clr.AddReference('PacBio.Instrument.Axis')
clr.AddReference("PacBio.Instrument.Alignment")  
clr.AddReference('PacBio.Instrument.Interfaces.Movement')
clr.AddReference('PacBio.Instrument.RT')
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

from PacBio.Instrument.Alignment import *
from PacBio.Instrument.Alignment.Test import *
from System import *
from System.Collections import *
from System.Collections.Generic import *
from System.Drawing import *
from PacBio.Instrument.Camera import *
from PacBio.Instrument.Alignment import *
from PacBio.Instrument.Halcon import *

bsbrcamera = instrument.BSBR.Camera
bsbrillum = instrument.BSBR.Illuminator

obts = instrument.ObjectBrowserTestService

def InitTEC():
    global clamp
    loop = clamp.TempControl.Ctrl
    loop.SetOMax(0, 900)
    loop.SetOMin(0, -900)
    loop.SetKc(0, 1)

    loop.SetSetpoint(0, 22)
    
    # loop.SetEnable(0, True)

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
    
coherent = instrument.IlluminationPath[642].Laser
mpb = instrument.IlluminationPath[532].Laser
camera = instrument.CollectionPath[538].Camera
robotIllum = instrument.Robot.ZIlluminator

def moveZ(dest):
    print "Setting Z", dest
    z.TargetPosition = dest
    MovementException.Check(z.WaitForMove())

def testZ(z):
    for i in range(-4, 4):
        moveZ(z + i * 100e-6)
    
def stressZ():
    stage.Axis.FindIndex()
    MovementException.Check(stage.Axis.WaitForMove())
    zv = z.CurrentPosition
    for i in range(1, 100):
        testZ(zv) 
        
def WorkflowDoneHandler(sender, args):
    print 'WorkflowDone event: ' + str(args.DoneType)
    if args.Exception is not None:
        print '  ' + str(args.Exception)
    if args.AlarmEvent is not None:
        print '  ' + args.AlarmEvent.Name
        print '  ' + str(args.AlarmEvent.Severity)
        print '  ' + str(args.AlarmEvent.Exception)

def WaitForUserHandler(sender, args):
    print 'WaitForUser event - state: ' + str(args.State)

#def testBsbrRef():
    #wf.WorkflowDone += WorkflowDoneHandler
    #wf.WaitForUser += WaitForUserHandler

#wf = instrument.ToolFactory.BsbrReferenceWorkflow
#testBsbrRef()

v1 = relay1.VectorAxis
v2 = v1.VectorAxis
v3 = v2.Target

def V1TargetPositionChanged(sender, args):
    print 'V1 TargetPositionChanged - position: ' + str(v1.TargetPosition)

#v1.TargetPositionChanged += V1TargetPositionChanged
    
def V2TargetPositionChanged(sender, args):
    print 'V2 TargetPositionChanged - position: ' + str(v2.TargetPosition)
    
#v2.TargetPositionChanged += V2TargetPositionChanged

def V3TargetPositionChanged(sender, args):
    print 'V3 TargetPositionChanged - position: ' + str(v3.TargetPosition)

#v3.TargetPositionChanged += V3TargetPositionChanged
  

#view(instrument.ChipAlignment)

#view(instrument.CreateFluorescenceMaximizer(538, 642))

#view(instrument.IlluminationPath[532].SteeringMirrors)

#view(instrument.IlluminationPath[532].BeamSteeringMirrors)

#view(instrument.IlluminationPath[532].BeamSteeringMirrors.SteeringMirrorAssemblies[0])

#view(instrument.IlluminationPath[532].CameraSWA)

#leveler = instrument.Tools["illuminationLeveler"]
#view(leveler)

#ns=instrument.ToolFactory.NanoslitAlignment
#view(ns)

#ti=instrument.Illuminator
#view(ti)

#opt=instrument.ToolFactory.GetLaserSteeringOptimizer(Laser.Green)

#view(cas2)

def VolScanAnalyzerTest():
    vsa = VolumeScanAnalyzer.Instance
    vsa.Submit("A")    
    vsa.Submit("B")
    vsa.Submit("C")
    vsa.Submit("D")
    
    vsa.WaitForAnalysis("A")
    vsa.WaitForAnalysis("B")
    vsa.WaitForAnalysis("C")
    
    vsa.Submit("E")
    vsa.Submit("F")
    
    vsa.Submit("G")
    vsa.Submit("H")

instrument.ToolFactory.BsbrReferenceWorkflow2.SimulateResults=True

instrument.ToolFactory.OpticsHealthWorkflow.SimulateResults=True
    
    
    