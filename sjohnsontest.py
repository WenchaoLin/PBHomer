clr.AddReference("PacBio.Instrument.Acquisition")

from PacBio.Instrument.Interfaces.Acquisition import DyeInfo
from PacBio.Common.IO import FileMoverType, RemoteCommandMode, RsyncFileMover
from System.Collections.Generic import Dictionary

# setup homer to use a springfield toolbox of my choosing
# especially useful for a windows homer
def setup_sptb(instrument, exe):
  sptb = instrument.Children['SpringfieldToolboxSvc'].Toolbox
  sptb.ExeFileName = exe
  sptb.ExePrefix = ''

# setup putty pscp access in calibration use of SIA
def setup_scp(instrument):
  sia = instrument.AcqCalibration.siaUtils
  sia.CopyCommand = 'pscp'
  sia.NRTHostName = 'mp-homer102'

# cook up a fake dye for testing
def fake_dye():
  dye = DyeInfo()
  dye.DyeLabel = 'SoylentGreen'
  dye.Base = 'T'
  dye.Nucleotide = 'dT6P'
  dye.Wavelength = 555.0
  dye.DyeConcentration = 0.5
  return dye

def anyoldchip():
  return 'SpringfieldPANE_L16_L00_L31_L32_LOOK1_DISTD_NN_TYPE_CALIB_Laurel'

def blah():
  dict = Dictionary[str,str]()
  dict['Comment']='Test of calibration tools'
  return dict

def pd(d):
   for item in d:
      print item

def pp(d,count):
   for item in range(0,count):
      print d[item]

def setup_copy():
   fileMover = RsyncFileMover(0, False, RemoteCommandMode.PasswordlessSsh)
   return fileMover

def setup_copy_instrument():
   fileMover = RsyncFileMover(0, False, RemoteCommandMode.Instrument)
   return fileMover
