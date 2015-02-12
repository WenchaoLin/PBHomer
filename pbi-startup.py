print "Labtech startup script initializing..."

import clr

from PacBio.Instrument.Interfaces import *
from PacBio.Instrument.Interfaces.Movement import *
from PacBio.Instrument.Interfaces.Alignment import *
from PacBio.Instrument.Alignment.Controllers import *
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

#some canned_scripts
from AlignmentUtils import *
from StageLevelUtil import *
from SimpleStack import *

#enable debug info for alignment
LogFilter.Instance.AddThresholdFilter("PacBio.Instrument.Alignment.*", ".*", LogLevel.DEBUG, False)
