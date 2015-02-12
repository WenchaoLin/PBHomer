#
# Don's standard homer debug environmnet
#

import clr
import time
from PacBio.Instrument.Interfaces import *
from PacBio.Instrument.Interfaces.Movement import *
from PacBio.Instrument.Interfaces.Alignment import *
from PacBio.Instrument.RT import *
from PacBio.Instrument.Devices import *
from PacBio.Common.Diagnostics import *
from PacBio.Common.Numeric import *
from PacBio.Common.IO import *
from System.Collections.Generic import *
from System.Drawing import *
from PacBio.Instrument.Camera import *
from PacBio.Instrument.Alignment import *
from PacBio.Instrument.Alignment.Test import *
from PacBio.Instrument.Halcon import *
from PacBio.Common.Utils import *

#ref our alignment test stuff    
alignmentTestDir = exedir + "/../../../PacBio/Instrument/Alignment/Test/"
sys.path.append(alignmentTestDir)

#ref the composition directory
compositionDir = exedir + "/../../../PacBio/Instrument/Homer/composition"
sys.path.append(compositionDir)

#ref the canned_scripts directory
sys.path.append(cannedScriptDir + "/Alignment")

from TestSelectorsPy import *

from alignment import *

from AlignmentUtils import *

# GPIOBoard = "10.10.5.155" 
# gpio = RTBoard.Get(IGPIO, GPIOBoard, "/gpio")

#block decldata
#Note that this only applies after startup since the scripts are run after start
#LogFilter.Instance.AddFilter("PacBio.Common.Data.Decl.*", ".*", ".*", True);

illumPath = instrument.IlluminationPath[532]
shutter = illumPath.Shutter
voa = illumPath.VOA
psb = illumPath.PSB
doe = illumPath.DOE
beamExpander = illumPath.BeamExpander
beamSteering = illumPath.BeamSteeringMirrors
rlg = illumPath.RelayLensGroup
swa = illumPath.SWA

from PacBio.Common.Services import *

svcRegistry = ServiceRegistry.Instance

def ShowDiagSvcs() :
    type = clr.GetClrType(IRunDiags)
    diagSvcs = svcRegistry.FindService(type)
    for svc in diagSvcs :
        print "Diag Service: ", svc
        
def testSWA() :
    """ Run the SWA through its paces"""
    for i in range(swa.SWATransform.Min,swa.SWATransform.Max):
	    pass
 
            
sl = None
qdc = None
results = None
selector = None


def testStageLeveler() :
    global qdc
    global sl, results, selector
    
    #get the QuickAndDirtyCamera built - only expensive the first time
    qdc = makeQdc(instrument)
#doesn't work yet
#    view(qdc)
        
    #get our leveler 
    #instrument leveler not working for some reason....
    if True: #try2
        sl = StageLeveler(qdc, instrument.Stage.Axis)   #make a new custom leveler 
        sl.Initialize()
    else:
        sl = instrument.Children["stageLeveler"]        #grab the leveler the instrument has
    
    sl.Params.FocalControlParams.NumColumnsX = 20
    sl.Params.FocalControlParams.NumColumnsY = 20
    sl.InitialCenterOfFocus = XYZabc( 0,0, Units.UM(5), 0,0,0)
    sl.InitialNegEpsilonZ = Units.UM(50)
    sl.InitialPosEpsilonZ = Units.UM(50)
    sl.MaxIterations = 1    #make it fast
    sl.StepsPerStack = 10

    #do the level (can specify a camera)
#    sl.DoLevel()
    sl.Level() 
    
    #our complete stack
    results = sl.StackResults
    
    #the selector utility class
    selector = sl.ResultSelector
    
    #all the waypoints
    selector.Waypoints
    
    #all the results
    selector.StackResults
    
    #pull all the Z's out from the stack of Axis positions
    zPosition = selector.Position(2)    
    
    #plotter
    plotter = SimplePlot()

    numRegions = sl.VerticalColumnsX * sl.VerticalColumnsY    
    if True:
        #pull out several focal scores
        sums = selector.SelectedResults[float](lambda r: r.RegionStat.IntensitySum, range(0, numRegions))
        multiZ = (zPosition,) * len(sums)
        plotter.MultiPlot2D[float](multiZ, sums)
    else:
        #old style, but effective
        for i in range(0,numRegions):
            #using a delegate, pull a particular focal score out from the stack
            focus = selector.SelectedResults[float](lambda r: r.RegionStat.IntensitySum, i)    
            plotter.AddPlotData(zPosition, focus)    
        plotter.Plot()
    

from PacBio.Instrument.Interfaces import *
from PacBio.Common.Remoting import *
def showRemotingMethods():
    pi = Methods.GetAllProperties(OttoFrame)
    for p in pi:
        print str(p.Name) + " " + str(p.CanRead) + " " + str(p.GetGetMethod())

def stageTest (numRuns):
    stage.AutoAxis = True
    for i in range(0,numRuns):
        start = stage.Axis.CurrentPosition
        print "Move: ", i
        vZero = (0,0,0,0,0,0)
        vExtent = (20e-6, 20e-6, 40e-6, 5e-6, 5e-6, 5e-6)
        
        stage.Axis.BeginMove(MoveType.Absolute, vZero)
        stage.Axis.WaitForMove()
        
        stage.Axis.BeginMove(MoveType.Absolute, vExtent)
        stage.Axis.WaitForMove()
        
    stage.Axis.BeginMove(MoveType.Absolute, start)



def showChip():
    view(qdc.Snapshot(True))
    
#alignment utilities
#execfile(cannedScriptDir + '/Alignment/StageLevelUtil.py')

 
    
    