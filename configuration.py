import clr

import System
from PacBio.Common.Numeric import *

clr.AddReference("PacBio.Instrument.Homer")
from PacBio.Instrument.Homer import HomerConfigurationService

clr.AddReference("PacBio.Common.Data.Decl")
from PacBio.Common.Data.Decl import DeclDataClassification


def configRalph():
	
	homerConfigSvc = HomerConfigurationService.Instance

	homerConfigSvc.RTOPT532='172.31.128.22'
	homerConfigSvc.RTOPT642='172.31.128.23'
	homerConfigSvc.RTSTAGE='172.31.128.21'
	homerConfigSvc.RTWDECT='172.31.128.24'
	homerConfigSvc.RTWDECH='172.31.128.25'
	homerConfigSvc.RTROBOT='fixme'
	homerConfigSvc.OTTOHOST='mp-nrt04'
	homerConfigSvc.BSBRCAMGUID='a47011109401b'

	homerConfigSvc.NOCALLOTTO=False
	homerConfigSvc.NOSTAGE=False
	homerConfigSvc.NOWDEC=False
	homerConfigSvc.NOROBOT=True
	homerConfigSvc.NOOPTICS=True

        homerConfigSvc.EditDeclRepository.UpdateRepository(DeclDataClassification.Any, False)

	print "Done with ralph config - database updated"


def configNelson():
	

	print "Done with Nelson cal - database updated"    
	
