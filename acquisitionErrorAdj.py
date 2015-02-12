import clr

clr.AddReference("PacBio.Instrument.Acquisition")

from PacBio.Instrument.Acquisition import *
from PacBio.Instrument.Homer import HWConfig
from PacBio.Instrument.Interfaces.Homer import InstrumentContext
from PacBio.Instrument.Interfaces import DoeLayout
from PacBio.Instrument.Interfaces import RTAlarmSeverity


from System.Collections.Generic import List

def AdjustAcquisitionErrorSeverity() :

    instrument = InstrumentContext.Instrument
    if ( instrument.HWConfig.DOE == DoeLayout.RS2 ) :
        # for 150K, do not assume a DataCameraStreaming.Abort
        # is grounds for a full run abort (only a chip abort)
        rules = List[AlarmRule[RTAlarmSeverity]]()
        kvp = AlarmRule[RTAlarmSeverity]("DataCameraStreaming.Abort",RTAlarmSeverity.FATAL)
        rules.Add(kvp)
        kvp = AlarmRule[RTAlarmSeverity]("DataCameraStreaming.Overrun",RTAlarmSeverity.FATAL)
        rules.Add(kvp)

        instrument.Acquisition.ResultProcessor.RunAbortInclusiveSeverityRules=rules

