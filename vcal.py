from PacBio.Instrument.Homer import *
from PacBio.Instrument.Vision import *
from PacBio.Instrument.Robot import *
from PacBio.Common.Numeric import *
from PacBio.Common.IO import *
from PacBio.Instrument.Interfaces import *
from PacBio.Instrument.Interfaces.Fluidics import *
from PacBio.Instrument.Interfaces.Homer import *
from PacBio.Instrument.Interfaces.Movement import *
from PacBio.Instrument.Interfaces.Vision import *
from PacBio.Instrument.RT import *
from System import *
from System.IO import *
from System.Xml.Serialization import XmlSerializer
import copy
import time
import clr
import string
from HalconDotNet import *
from robotics import *

# Calibrators for all of the MV cameras.

#
# facilitator functions for Mfg
#
cal=None

def focuson():
	cal.DisplayFocusMetric(True)
	
def focusoff():
	cal.DisplayFocusMetric(False)
	
def zcam():
	global cal
	cal=RobotZCal()
	cal.ResetCalibrationImages()
	cal.Cam.DisplayStart()
	return

def stageleftcam():
	global cal
	cal=StageLeftCal()
	cal.ResetCalibrationImages()
	cal.Cam.DisplayStart()
	return

def stagerightcam():
	global cal
	cal=StageRightCal()
	cal.ResetCalibrationImages()
	cal.Cam.DisplayStart()
	return

def stagestereocams():
	global cal
	cal=StageStereoCal()
	cal.ResetCalibrationImages()
	cal.Other.ResetCalibrationImages()
	cal.Cam.DisplayStart()
	cal.Other.Cam.DisplayStart()
	return

def cpsleftcam():
	global cal
	cal=CPSLeftCal()
	cal.ResetCalibrationImages()
	cal.Cam.DisplayStart()
	return

def cpsrightcam():
	global cal
	cal=CPSRightCal()
	cal.ResetCalibrationImages()
	cal.Cam.DisplayStart()
	return

def cpsstereocams():
	global cal
	cal=CPSStereoCal()
	cal.ResetCalibrationImages()
	cal.Other.ResetCalibrationImages()
	cal.Cam.DisplayStart()
	cal.Other.Cam.DisplayStart()
	return

def grab():
	cal.Cam.DisplayStop()
	cal.CheckedAddImage()
	print cal.CalibImages.Count, "images captured"
	cal.Cam.DisplayStart()
	return
	
def stopcam():
	cal.Cam.DisplayStop()
	cal.Cam.Hide()
	return
	
def stopcams():
	cal.Cam.DisplayStop()
	cal.Cam.Hide()
	cal.Other.Cam.DisplayStop()
	cal.Other.Cam.Hide()
	return

def stereograb():
	cal.Cam.DisplayStop()
	cal.Other.Cam.DisplayStop()
	cal.CheckedAddBoth()
	print cal.CalibImages.Count, "images captured"
	cal.Cam.DisplayStart()
	cal.Other.Cam.DisplayStart()
	return

def calibrate():
	cal.Cam.DisplayStop()
	try:
		cal.Calibrate()
	except:
		print "Calibration FAILED"
	else:
		print "Calibration PASSED"
	return

def stereocalibrate():
	cal.Cam.DisplayStop()
	cal.Other.Cam.DisplayStop()
	try:
		cal.Calibrate()
	except:
		print "Calibration FAILED"
	else:
		print "Calibration PASSED"
	return

def exportzcal():
	vt = InstrumentContext.Instrument.Robot.VisionTools
	if not vt.Cameras.ContainsKey(CameraNames.RobotZ):
		print "# No Z camera found"
		return
	cam = vt.RealCamera(CameraNames.RobotZ)
	fhandle = open("/home/astrolab/caldata/Z_" + cam.GUID + ".py", "w")
	ExportCameraCal(CameraNames.RobotZ, fhandle)
	fhandle.close()
	return

def exportcpscal():
	vt = InstrumentContext.Instrument.Robot.VisionTools
	if not vt.Cameras.ContainsKey(CameraNames.CPSLeft):
		print "# No CPS cameras found"
		return
	cam = vt.RealCamera(CameraNames.CPSLeft)
	fhandle = open("/home/astrolab/caldata/cps_" + cam.GUID + ".py", "w")
	ExportCameraCal(CameraNames.CPSLeft, fhandle)
	ExportCameraCal(CameraNames.CPSRight, fhandle)	
	fhandle.close()
	return

def exportstagecal():
	vt = InstrumentContext.Instrument.Robot.VisionTools
	if not vt.Cameras.ContainsKey(CameraNames.StageLeft):
		print "# No Stage cameras found"
		return
	cam = vt.RealCamera(CameraNames.StageLeft)
	fhandle = open("/home/astrolab/caldata/stage_" + cam.GUID + ".py", "w")
	ExportCameraCal(CameraNames.StageLeft, fhandle)
	ExportCameraCal(CameraNames.StageRight, fhandle)
	fhandle.close()
	return

#
# End Mfg stuff
#

def RobotZCal():
	vt = InstrumentContext.Instrument.Robot.VisionTools;
	cam = vt.RealCamera(CameraNames.RobotZ)
	cam.Gain = 0
	cam.Shutter = 2000
	cam.Show()
	
	cal = HALCONInteriorCameraCalibrator(cam)
	cal.Debug=True
	cal.Gain = 0
	cal.Brightness = 0
	cal.Shutter = "auto"
	cal.AutoExposure = 120
	cal.MarkThreshold = 70
	cal.CalibrationBounds = 0.05
	
	cam.Show(cal.Snap())
	return cal

def StageLeftCal():
	vt = InstrumentContext.Instrument.Robot.VisionTools;
	cam = vt.RealCamera(CameraNames.StageLeft)
	cam.Gain = 0
	cam.Shutter = 2000
	cam.StartCameraParams = (0.018, 0.0, 0.0, 0.0, 0.0, 0.0, 4.65e-006, 4.65e-006, 512.0, 384.0, 1024, 768)
	cam.Show()
	
	cal = HALCONInteriorCameraCalibrator(cam)
	cal.Debug=True
	cal.CaltabFile = "datafiles/caltab_10mm.descr"
	cal.Gain = 0
	cal.Brightness = 0
	cal.Shutter = "auto"
	cal.AutoExposure = 180
	cal.MarkThreshold = 100
	cal.CalibrationBounds = 0.10
	
	cam.Show(cal.Snap())
	return cal

def StageRightCal():
	vt = InstrumentContext.Instrument.Robot.VisionTools;
	cam = vt.RealCamera(CameraNames.StageRight)
	cam.Gain = 0
	cam.Shutter = 2000
	cam.StartCameraParams = (0.018, 0.0, 0.0, 0.0, 0.0, 0.0, 4.65e-006, 4.65e-006, 512.0, 384.0, 1024, 768)
	cam.Show()
	
	cal = HALCONInteriorCameraCalibrator(cam)
	cal.Debug=True
	cal.CaltabFile = "datafiles/caltab_10mm.descr"
	cal.Gain = 0
	cal.Brightness = 0
	cal.Shutter = "auto"
	cal.AutoExposure = 180
	cal.MarkThreshold = 100
	cal.CalibrationBounds = 0.10
	
	cam.Show(cal.Snap())
	return cal

def StageStereoCal():
	vt = InstrumentContext.Instrument.Robot.VisionTools
	
	lname = CameraNames.StageLeft
	rname = CameraNames.StageRight
	sname = CameraNames.StageStereo
	
	cpl = vt.RealCamera(lname)
	cpl.Gain = 0
	cpl.Shutter = 4000
	cpl.Show()
	
	cpr = vt.RealCamera(rname)
	cpr.Gain = 0
	cpr.Shutter = 4000
	cpr.Show()
	
	scal = HalconStereoCalibrator(cpl)
	scalo = HalconStereoCalibrator(cpr)
	scal.Other = scalo
	scalo.Other = scal
	scal.Debug=True
	scal.Other.Debug=True
	scal.MarkThreshold = 100
	scal.Other.MarkThreshold = 100
	scal.Gain = 0
	scal.Other.Gain = 0
	scal.Shutter = "auto"
	scal.Other.Shutter = "auto"
	scal.AutoExposure = 180
	scal.Other.AutoExposure = 180
	scal.CalibrationBounds = 0.25
	scal.Other.CalibrationBounds = 0.25
	scal.CaltabFile = "datafiles/caltab_10mm.descr"
	scal.Other.CaltabFile = "datafiles/caltab_10mm.descr"
	
	return scal

def CPSLeftCal():
	vt = InstrumentContext.Instrument.Robot.VisionTools;
	cam = vt.RealCamera(CameraNames.CPSLeft)
	cam.Gain = 0
	cam.Shutter = 2000
	cam.Show()
	
	cal = HALCONInteriorCameraCalibrator(cam)
	cal.Debug=True
	cal.Gain = 0
	cal.Brightness = 0
	cal.Shutter = "auto"
	cal.AutoExposure = 180
	cal.MarkThreshold = 70
	cal.CalibrationBounds = 0.05
	
	cam.Show(cal.Snap())
	return cal

def CPSRightCal():
	vt = InstrumentContext.Instrument.Robot.VisionTools;
	cam = vt.RealCamera(CameraNames.CPSRight)
	cam.Gain = 0
	cam.Shutter = 2000
	cam.Show()
	
	cal = HALCONInteriorCameraCalibrator(cam)
	cal.Debug=True
	cal.Gain = 0
	cal.Brightness = 0
	cal.Shutter = "auto"
	cal.AutoExposure = 180
	cal.MarkThreshold = 70
	cal.CalibrationBounds = 0.05
	
	cam.Show(cal.Snap())
	return cal

def CPSStereoCal():
	vt = InstrumentContext.Instrument.Robot.VisionTools
	
	lname = CameraNames.CPSLeft
	rname = CameraNames.CPSRight
	sname = CameraNames.CPSStereo
	
	cpl = vt.RealCamera(lname)
	cpl.Gain = 0
	cpl.Shutter = 4000
	cpl.Show()
	
	cpr = vt.RealCamera(rname)
	cpr.Gain = 0
	cpr.Shutter = 4000
	cpr.Show()
	
	scal = HalconStereoCalibrator(cpl)
	scalo = HalconStereoCalibrator(cpr)
	scal.Other = scalo
	scalo.Other = scal
	scal.Debug=True
	scal.Other.Debug=True
	scal.MarkThreshold = 100
	scal.Other.MarkThreshold = 100
	scal.Gain = 0
	scal.Other.Gain = 0
	scal.Shutter = "auto"
	scal.Other.Shutter = "auto"
	scal.AutoExposure = 180
	scal.Other.AutoExposure = 180
	scal.CalibrationBounds = 0.06
	scal.Other.CalibrationBounds = 0.06
	scal.CaltabFile = "datafiles/caltab_10mm.descr"
	scal.Other.CaltabFile = "datafiles/caltab_10mm.descr"
	
	return scal

def StereoDisplay(scal):
	d = MultiCameraDisplay(scal.Cam, scal.Other.Cam)
	d.Display()

def RobotHandEyeCal():
	return vt.HandEye["Robot-Z"]
	
def StageRobotHandEyeCal():
	cal = vt.HandEye["Robot-StageRight"]
	cal.Center = o.G1StagePos
	rc.TrapDoor.BeginOpen(True)
	rc.TrapDoor.EndMove()
	gp1.SetPosition(GripperState.Piercing)
	return cal
	
def CPSRobotHandEyeCal():
	return vt.HandEye["Robot-CPSRight"]

def VisualizeHandEye(cal, mag=100.0, outfile=None):
	sp = SimplePlot()
	sp.Style = "vector"
	sp.AddPlotData(cal.PCol.ToDArr(), cal.PRow.ToDArr(), cal.DCol.TupleMult(mag).ToDArr(), cal.DRow.TupleMult(mag).ToDArr())
	sp.Plot()
	sp.TerminalType = "png size 1280,1024"
	if outfile != None:
		sp.Command("set output \'" + outfile + "\'")
		sp.Plot()

def CalibrateShutterForCamera(camName):
	if not vt.Cameras.ContainsKey(camName):
		print "No camera named " + camName + ", skipping"
		return
	
	cam = vt.RealCamera(camName)
	cam.CalibrateShutter()

def CalibrateShutters():
	CalibrateShutterForCamera(CameraNames.StageLeft)
	CalibrateShutterForCamera(CameraNames.StageRight)
	CalibrateShutterForCamera(CameraNames.CPSLeft)
	CalibrateShutterForCamera(CameraNames.CPSRight)

def StringifyCameraParams(p):
	ret = "(";
	for i in range(0, p.Length):
		ret = ret + str(p[i]) + ", "
	
	ret = ret + ")";
	return ret;

def StringifyCameraPose(p):
	return "(" + str(p[0]) + ", " + str(p[1]) + ", " + str(p[2]) + ", " + str(p[3]) + ", " + str(p[4]) + ", " + str(p[5]) + ", \"" + p[6] + "\", \"" + p[7] + "\", \"" + p[8] + "\")"

def ExportCameraCal(cname, fhandle):
	if not vt.Cameras.ContainsKey(cname):
		print "# No camera with name " + cname
		return
	
	cam = vt.RealCamera(cname)
	print >>fhandle, "from robotics import *"
	print >>fhandle, "GUID = \"" + cam.GUID + "\""
	print >>fhandle, "cam = vt.RealCamera(\"" + cname + "\")"
	print >>fhandle, "if GUID != cam.GUID:"
	print >>fhandle, "	print \"GUID mismatch for " + cname + "\""
	print >>fhandle, "	print \"GUID \" + cam.GUID + \" found but should have been \" + GUID"
	print >>fhandle, "else:" 
	print >>fhandle, "	cam.CameraParams = " + StringifyCameraParams(cam.CameraParams)
	print >>fhandle, "	cam.CameraParamsError = " + str(cam.CameraParamsError)
	print >>fhandle, "	cam.CameraPose = " + StringifyCameraPose(cam.CameraPose)
	print >>fhandle, "	cam.CameraPoseError = " + str(cam.CameraPoseError)
	print >>fhandle, "	cam.Calibrate(\"CameraParams\")"
	print >>fhandle, "	cam.Calibrate(\"CameraParamsError\")"
	print >>fhandle, "	cam.Calibrate(\"CameraPose\")"
	print >>fhandle, "	cam.Calibrate(\"CameraPoseError\")"

def ExportAllCameraCalToHandle(fhandle):
	ExportCameraCal(CameraNames.RobotZ, fhandle)
	ExportCameraCal(CameraNames.StageLeft, fhandle)
	ExportCameraCal(CameraNames.StageRight, fhandle)
	ExportCameraCal(CameraNames.CPSLeft, fhandle)
	ExportCameraCal(CameraNames.CPSRight, fhandle)	

import sys
def ExportAllCameraCal():
	ExportAllCameraCalToHandle(sys.stdout)

def ExportAllCameraCalToFile(fname):
	fhandle = open(fname, "w")
	ExportAllCameraCalToHandle(fhandle)
	fhandle.close()
