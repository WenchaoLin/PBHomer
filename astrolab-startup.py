#
# astrolab's homer debug environmnet
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

#ref the acquisition script directory
sys.path.append(cannedScriptDir + "/Acquisition")

# from AlignmentUtils import *

# GPIOBoard = "10.10.5.155" 
# gpio = RTBoard.Get(IGPIO, GPIOBoard, "/gpio")

#block decldata
#Note that this only applies after startup since the scripts are run after start
#LogFilter.Instance.AddFilter("PacBio.Common.Data.Decl.*", ".*", ".*", True);

illumPath = instrument.IlluminationPath[532]
#shutter = illumPath.Shutter
#voa = illumPath.VOA
#psb = illumPath.PSB
#doe = illumPath.DOE
#beamExpander = illumPath.BeamExpander
#beamSteering = illumPath.BeamSteering
#rlg = illumPath.RelayLensGroup
#swa = illumPath.SWA

################################################################################

from PacBio.Common.Services import *

svcRegistry = ServiceRegistry.Instance

def ShowDiagSvcs() :
    type = clr.GetClrType(IRunDiags)
    diagSvcs = svcRegistry.FindService(type)
    for svc in diagSvcs :
        print "Diag Service: ", svc

sl = None
qdc = None
results = None
selector = None

################################################################################

from PacBio.Instrument.Interfaces import *
from PacBio.Common.Remoting import *

def showRemotingMethods():
    pi = Methods.GetAllProperties(OttoFrame)
    for p in pi:
        print str(p.Name) + " " + str(p.CanRead) + " " + str(p.GetGetMethod())

#alignment utilities
#execfile(cannedScriptDir + '/Alignment/StageLevelUtil.py')

################################################################################

from AcquisitionUtils import *

def DoNelsonDyeCal(frame_count, filename):
	camera_set = GetMaxRoiCameraSet('nrt-nelson.lab', '8082')
	DoIllumFrameCapture(camera_set)
	DoTraceExtraction(camera_set, 5, filename)

