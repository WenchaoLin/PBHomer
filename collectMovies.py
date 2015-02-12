# hack script to provide some basic movie functionality
# replace at your earliest convenience
from System.Drawing import *
from PacBio.Instrument.RT import *
from PacBio.Instrument.Interfaces import *
from System.Drawing import *
import System
from System.Threading import *
import System.Drawing

from PacBio.Instrument.Homer import *
from PacBio.Instrument.Interfaces import *
from PacBio.Instrument.Interfaces.Loader import *
from PacBio.Instrument.Interfaces.Homer import *
from PacBio.Instrument.Interfaces.Movement import *

from PacBio.Common.Diagnostics import *
from PacBio.Common.Numeric.Units import *
from PacBio.Common.Frames import *
from PacBio.Common.Data.Decl import *

instrument = InstrumentContext.Instrument

#FIXME:
nrtConn = '172.31.128.10:8082'


movies_cs =  RTBoard.Get(ICameraSet, nrtConn, "/cameraSet")
movies_c0 =  RTBoard.Get(ICameraSet, nrtConn, "/camera0")
movies_c1 =  RTBoard.Get(ICameraSet, nrtConn, "/camera1")
movies_c2 =  RTBoard.Get(ICameraSet, nrtConn, "/camera2")
movies_c3 =  RTBoard.Get(ICameraSet, nrtConn, "/camera3")
movies_c4 =  RTBoard.Get(ICameraSet, nrtConn, "/camera4")
movies_c5 =  RTBoard.Get(ICameraSet, nrtConn, "/camera5")
movies_c6 =  RTBoard.Get(ICameraSet, nrtConn, "/camera6")
movies_c7 =  RTBoard.Get(ICameraSet, nrtConn, "/camera7")

#original rect 
movies_defaultRect = Rectangle(0,0,2600,1096)
movies_movieRect = Rectangle(960,0,200,200)

movies_BSBR_defaultRect = Rectangle(0,0,2056,2056)
movies_BSBR_movieRect = Rectangle(1000,1000,100,100)

def setRect(xstart=960, ystart=0, xlength=200, ylength=200):
   global movies_movieRect
   movies_movieRect = Rectangle(xstart, ystart, xlength, ylength)

def setBSBRRect(xstart=1000, ystart=500, xlength=200, ylength=200):
   global movies_BSBR_movieRect
   movies_BSBR_movieRect = Rectangle(xstart, ystart, xlength, ylength)

movies_subframe = ''
movies_camset = ''

def doMovie(name, frames, cam=3, sensor=0, exposure=0.001, rect=''):
   global movies_cs
   global movies_c0
   global movies_c1
   global movies_c2
   global movies_c3
   global movies_c4
   global movies_c5
   global movies_c6
   global movies_c7
   global movies_movieRect
   global movies_defaultRect
   global movies_camset
   global movies_subframe
   global nrtConn
   if not rect:
      rect = movies_movieRect
   try:
      movies_cs.AbortCapture()
   except:
      pass
   Thread.Sleep(1000)
   if sensor != 0 and sensor != 1:
      print "sensor must be 0 or 1"
      return
   # camera is the otto sensor number of 0-7
   if cam == 1:
      if sensor == 0:
         movies_camset = movies_c0
         camera = 0
      elif sensor == 1:
         movies_camset = movies_c1
         camera = 1
   elif cam == 2:
      if sensor == 0:
         movies_camset = movies_c2
         camera = 2
      elif sensor == 1:
         movies_camset = movies_c3
         camera = 3
   elif cam == 3:
      if sensor == 0:
         movies_camset = movies_c4
         camera = 4
      elif sensor == 1:
         movies_camset = movies_c5
         camera = 5
   elif cam == 4:
      if sensor == 0:
         movies_camset = movies_c6
         camera = 6
      elif sensor == 1:
         movies_camset = movies_c7
         camera = 7
   else:
      print "cam must be 1, 2, 3, or 4"
      return

   print "Setting up movie options: exposure %f, Rect %s, Readout Rate: %s" % (exposure, movies_movieRect.ToString(), "280 MHz")
   movies_camset.SetDouble("ExposureTime", exposure)
   movies_camset.GrabRect = rect
   movies_camset.SetEnumString("PixelReadoutRate", "280 MHz")
   if movies_subframe:
      print "removing old subframe object"
      movies_subframe.Enabled = False
   print "getting subframe object"
   movies_subframe = RTBoard.Get(ICameraSubframe, nrtConn, "/camera%s/subframe2" % camera)
   movies_subframe.Enabled = True
   movies_subframe.Stride = 0
   movies_subframe.GrabRect = movies_camset.GrabRect
   movies_subframe.MovieFileName = "%s.mov.h5" % name
   print "Starting movie with %d frames" % frames
   movies_camset.StartCapture(frames)

def doCleanup():
   #to restore everything back
   global movies_defaultRect
   global movies_camset
   global movies_subframe
   global movies_cs
   try:
      movies_cs.AbortCapture()
   except:
      pass
   Thread.Sleep(1000)
   if movies_camset:
      movies_camset.GrabRect = movies_defaultRect
      movies_camset.SetDouble("ExposureTime", 0.1)
      movies_camset.SetEnumString("PixelReadoutRate", "200 MHz")
   if movies_subframe:
      movies_subframe.Enabled = False
   movies_cs.StartCapture(0)

def doBSBRCleanup():
   global movies_BSBR_defaultRect
   global instrument
   cam = instrument.BSBR.Camera.Cam
   cam.AOI = movies_BSBR_defaultRect
   instrument.BSBR.CameraSet.CrudeMovieCapture('resetBSBR', 1, 1,-1)

def doBSBRMovie(name, frames, exposure=0.5, rect=''):
   global movies_BSBR_movieRect
   global instrument
   cam = instrument.BSBR.Camera.Cam

   if rect:
      cam.AOI = rect
   else:
      cam.AOI = movies_BSBR_movieRect

   mTime = frames * exposure

   print "Starting BSBR movie: exposure %f, Rect %s, frames: %f, time: %f" % (exposure, cam.AOI.ToString(), frames, mTime)
   instrument.BSBR.CameraSet.CrudeMovieCapture(name, mTime, exposure,-1)

