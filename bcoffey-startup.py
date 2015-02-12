#
# Brendan's homer debug environmnet
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
from PacBio.Common.Scripting import *

#ref our alignment test stuff    
alignmentTestDir = exedir + "/../../../PacBio/Instrument/Alignment/Test/"
sys.path.append(alignmentTestDir)

#ref the composition directory
compositionDir = exedir + "/../../../PacBio/Instrument/Homer/composition"
sys.path.append(compositionDir)

systemTestDir = exedir + "/canned_scripts/InstrumentTests/src"
sys.path.append(systemTestDir)

#ref the canned_scripts directory
# sys.path.append(cannedScriptDir + "/Alignment")

#ref the acquisition script directory
#   sys.path.append(cannedScriptDir + "/Acquisition")

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

################################################################################
#
# Profiling and optimization stuff
#

# A series of square ZMW ROIs of increasing size

roi_50		= make_cs_zmw_roi(50)
roi_1000	= make_cs_zmw_roi(1000)
roi_5000	= make_cs_zmw_roi(5000)
roi_10000	= make_cs_zmw_roi(10000)
roi_15000	= make_cs_zmw_roi(15000)
roi_20000	= make_cs_zmw_roi(20000)
roi_25000	= make_cs_zmw_roi(25000)

################################################################################

allowEarlyStarts()
i.FSM.SkipStabilization=True
# instrument.Acquisition.Params.ComponentControl='Pre;off;0:n;0:n|Post;off;0:n;0:n|Gridder;off;0:n;0:n'
pc = PipelineController.Instance
