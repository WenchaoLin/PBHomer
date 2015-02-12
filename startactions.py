#
# startactions.py
#
# Runs once on instrument startup, independent of the shell
# Runs after instrument composition and configuration, but
# it runs before device init and warmup/diagnostics
#
# See http://smrtwiki.nanofluidics.com/wiki/Patches
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
from HomerApp import *

# BSBR useful stuff
clr.AddReference("PacBio.Instrument.BSBR")
from PacBio.Instrument.BSBR import *

logger = DiagManager.LogManager.LocalLogger("HomerProgram.")
logger.Log(ProgramLogEvent("Loading PacBio startactions.py..."))

#
# Temporary logging of axis positions for Don
#

def PerfMonSetup():
    #Setup the PerfMon's we want 
    instrument = InstrumentContext.Instrument
    axisList = []
    if instrument.CollimatorLens is not None:
        axisList.append(instrument.CollimatorLens.VectorAxis)
    for cp in instrument.CollectionPath.Values:
        axisList.append(cp.ImageLens.VectorAxis)
    for path in instrument.IlluminationPath.Values:
        axisList.append(path.DOE.VectorAxis)	
        axisList.append(path.RelayLensGroup.VectorAxis)	
        axisList.append(path.SWA.VectorAxis)
    if (instrument.BSBR is not None) and (instrument.BSBR.Focus is not None):
        axisList.append(instrument.BSBR.Focus.VectorAxis)
    if (instrument.Stage is not None):
        axisList.append(instrument.Stage.Axis)
    
    if instrument.Children.ContainsKey('illuminationLeveler'):
        ill = instrument.Children['illuminationLeveler']

    if instrument.Children.ContainsKey('chipAlignment2Svc'):
        cas2 = instrument.Children['chipAlignment2Svc']
        cas2.PolledPerfMonList.Add(instrument.ChipClamp.GetPerfMon("MostRecentVacuumPurge"))
        for axis in axisList:
            try:
                cas2.PolledPerfMonList.Add(axis.GetPerfMon("CurrentPosition"))
            except Exception, detail:
                cas2.Logger.Error("Failed adding PerfMon: " + str(dev) + ": " + str(detail) )

# Temporary logging of certain axes

logger.Log(ProgramLogEvent("Starting PerfMons for certain axes"))
PerfMonSetup()

#
# Bug 8904 - Temporary workaround
# Requires: scripts/robotics.py
#

#logger.Log(ProgramLogEvent("No longer installing bogus pipette cal."));
from robotics import *
logger.Log(ProgramLogEvent("Installing bogus pipette cal - temporary hack until http://bugzilla.nanofluidics.com/show_bug.cgi?id=8904 is verified"))
pipetteIdealCalib(pp0, "Aqueous", 1250, 125)
pipetteIdealCalib(pp1, "Aqueous", 1250, 125)
pipetteIdealCalib(pp0, "Glycerol", 500, 50)  
pipetteIdealCalib(pp1, "Glycerol", 500, 50)
