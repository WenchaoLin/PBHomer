import clr
import os
import util
import exceptions
import System
import itertools

clr.AddReference("PacBio.Instrument.RobotPlus")

from PacBio.Instrument.Interfaces.Movement import *
from PacBio.Instrument.Interfaces.Vision import *
from PacBio.Instrument.Vision import *
from PacBio.Instrument.Interfaces.Homer import InstrumentContext
from PacBio.Common.Numeric import *
from HalconDotNet import *
from protocols import *

# copied from robotics.py
i = InstrumentContext.Instrument
r = InstrumentContext.Instrument.Robot
rc = r.RControl
xy = InstrumentContext.Instrument.Robot.XYAxes
z = InstrumentContext.Instrument.Robot.ZAxes
vt = InstrumentContext.Instrument.Robot.VisionTools

def SetBarcodeForChipStrip(num):
	i.ChipsTipsDrawer.SetManualBarcode(MVLocationName.ChipStrip + MVLocationName.SeparatorStr + str(num), CreateManualBarcode('ChipStripFCR'))

# Loads a full set of inventory so that all plates can be used during simulation/testing.
def LoadSimInventory():
	DeleteInventoryData()
	vt.Oracle.ComputePositions()
	ImportSS('bin/Debug/Protocols/oneWellFCR.csv')
	
	# Fill with Chips
	for stripNo in range(0, i.ChipsTipsDrawer.ChipTray.ChipStripCapacity-1):
		SetBarcodeForChipStrip(stripNo)
	i.ChipsTipsDrawer.LoadAllPlates()
	
	# Fill Sample Tubes and Reagent Tubes
	i.TemplateReagentDrawer.SetManualBarcode('ReagentPlate0', CreateManualBarcode('DWPReagentPlate8FCRFinal') )
	i.TemplateReagentDrawer.SetManualBarcode('ReagentTube0-0', CreateManualBarcode('ShallowTube') )
	i.TemplateReagentDrawer.SetManualBarcode('ReagentTube0-1', CreateManualBarcode('ShallowTube') )
	i.TemplateReagentDrawer.SetManualBarcode('ReagentPlate1', CreateManualBarcode('DWPReagentPlate8FCRFinal') )
	i.TemplateReagentDrawer.SetManualBarcode('ReagentTube1-0', CreateManualBarcode('ShallowTube') )
	i.TemplateReagentDrawer.SetManualBarcode('ReagentTube1-1', CreateManualBarcode('ShallowTube') )
	i.TemplateReagentDrawer.SetManualBarcode('SampleTube-0', CreateManualBarcode('ShallowTube') )
	i.TemplateReagentDrawer.SetManualBarcode('SampleTube-1', CreateManualBarcode('ShallowTube') )
	i.TemplateReagentDrawer.LoadAllPlates()
	
	# Fill TipBoxes
	i.ChipsTipsDrawer.PipetteTipTray.FillBoxes()
	
	# So we can use pipettors.
	r.Pipettors[Pipette.Pipette1].FluidicsTag= 'simulated'
	r.Pipettors[Pipette.Pipette2].FluidicsTag= 'simulated'

def LocalDebug():
	os.environ['DISPLAY'] = "127.0.0.1:0.0"	
	Imager.DebugStatic = True
	AppSettings.Instance["VisionIncludes"] = "FCRClamp"
	LoadFiducialState()
	
# For now save only Fiducials.
# Will save StereoFinders next
# Remember to set ImageLogDirStatic prior to use
# Imager.ImageLogDirStatic = "C:\\data\\homerstate\\Fiducials"
def SaveFiducialState():
	if None == Imager.ImageLogDirStatic:
		print 'I don\'t know where to save the data to.	Did you forget to set Imager.ImageLogDirStatic? '
		return
	for entry in vt.Fiducials:
		f = entry.Value 
		label = entry.Key
		print('saving ' + label + ' state.')
		f.LogCurrent()

# Set up fake SimMVCameras for every camera as placeholders so we can load the fiducials 
# Use RecoverLogged to load old data for testing.
from vision_springfield import *
from ct_fiducials import *
from cp_fiducials import *
from rl_fiducials import *
def LoadFiducialState():
	vt.Cameras[CameraNames.RobotZ]		= HALCONCameraWrapper(SimMVCamera(HImage("byte", 1, 1))) 
	vt.Cameras[CameraNames.CPSLeft]	 = HALCONCameraWrapper(SimMVCamera(HImage("byte", 1, 1))) 
	vt.Cameras[CameraNames.CPSRight]	= HALCONCameraWrapper(SimMVCamera(HImage("byte", 1, 1))) 
	vt.Cameras[CameraNames.CPSStereo]	= HALCONCameraWrapper(SimMVCamera(HImage("byte", 1, 1))) 
	vt.Cameras[CameraNames.StageLeft]	= HALCONCameraWrapper(SimMVCamera(HImage("byte", 1, 1))) 
	vt.Cameras[CameraNames.StageRight]	= HALCONCameraWrapper(SimMVCamera(HImage("byte", 1, 1))) 
	vt.Cameras[CameraNames.StageStereo] = HALCONCameraWrapper(SimMVCamera(HImage("byte", 1, 1)))
	
	# Set config
	config = HomerConfigurationService.Instance.GetConfig(ConfigName.VisionIncludes)
	configItems = config + " LPRNest"
	HomerConfigurationService.Instance.SetConfig(ConfigName.VisionIncludes, configItems)

	# Make the fiducials.
	# Find some way of basing the fiducials to be created based on the files available on the
	# system
	MakeTransforms(vt)
	MakeTipNestFiducials(vt, rc.XYAxes)
	MakeFCRChipPrepFiducials(vt, rc.XYAxes)
	MakeChipTrayFiducials(vt, rc.XYAxes)
	MakeReagentLoaderFiducials(vt, rc.XYAxes)
	# Will need to initialize models because at time of creation, the camera parameters don't
	# have camera params.
	MakeStereoTools(vt)
	TipNestBetaParams(vt)
	
def SetFiltersForRobotControl ():
	LogFilter.Instance.AddFilter("svc:/instrument/robot/*", ".*", ".*", False)
	LogFilter.Instance.AddFilter("PacBio.Common.Services.ServiceBase", ".*", ".*", True)
	LogFilter.Instance.AddFilter("Python script command", ".*", "DEBUG", True)
	LogManager.Instance.SetConsoleLevel(LogLevel.TRACE)

# Testing fiducial finding over many iterations
def TestStageFinding(fileName, iterations, f):
	output = file(fileName, "w")

	calculatedPoses = []
	calculatedTrans = []

	for i in range(0, iterations):
		f.AcquireObject()
		calculatedPoses.append(f.PoseRecover.CameraPose)
		calculatedTrans.append(f.ObjectPositionRight)
		print("Iteration " + str(i) + ": ")
		print(f.PoseRecover.CameraPose)
		print(f.ObjectPositionRight)
		print("")
		
	#export translations and poses into file for easy parsing.	
	output.write("[");
	for i in range(0, iterations):
		output.write(", ".join([str(calculatedPoses[i][s]) for s in range(0, 6)]))
		output.write(", ")
		output.write(", ".join([str(s) for s in calculatedTrans[i]]))
		output.write(";\n")
	
	output.write("]");
	output.close();
	
import re
import os 
def DatesFromFiles(name, path):
	files = os.listdir(path)	
	dates = []
	for fi in files:
		m = re.search(name + '-(\d{6}_\d{6})-LastImage.tiff', fi)
		if m: 
			dates.append(m.group(1))
	return dates

def TestTipNests():
	ff = ['TipNest-0', 'TipNest-1']
	paths = ['C:\\data\\testfiducials\\failed\\tipnest\\42161',
		'C:\\data\\testfiducials\\failed\\tipnest\\42177',
		'C:\\data\\testfiducials\\failed\\tipnest\\42184',
		'C:\\data\\testfiducials\\failed\\tipnest\\42185',
		'C:\\data\\testfiducials\\failed\\tipnest\\42186']
	return TestFiducials(ff, paths)

def TestReagentLoaders():
	suffixes = ['0', '0-1', '0-2', '0-3', '1', '1-1', '1-2', '1-3', '2', '2-1', '2-2', '2-3']
	ff = ('ReagentLoader-' + str(k) for k in suffices )
	# Would be good to load some known good data in 0, 1, 2 first.
	# Current logging procedures do not store parent fiducial nor the robot positions
	# making exact recovery of the state at time of failure not possible.
	# For now, loading beta fids first.
	paths = ['C:\\data\\ReagentLoaderBeta\\', 
			 'C:\\data\\ReagentLoaderFCR\\',
			 'C:\\data\\Sample Plate Riser Fiducials\\', 
			 'C:\\data\\ReagentLoaderFails-134\\', 
			 'C:\\data\\ReagentLoaderFails-136\\', 
			 'C:\\data\\ReagentLoaderFails-130\\', 
			 'C:\\data\\ReagentLoader Fails\\']
	return TestFiducials(ff, paths)

def TestFiducials(fiducialfinders, paths):
	errorFiles=[]
	for path in paths:
		for f in fiducialfinders:
			errorFiles += TestFiducial(f, path)
	return errorFiles
	
def TestFiducial(name, path):
	errorFiles = []
	fiducial = vt.Fiducials[name]
	dates = DatesFromFiles(name, path)

	for date in dates:
		error = -1
		message = ""
		calBounds = fiducial.CalibrationBounds
		try :
			fiducial.CalibrationBounds = 2.0
			fiducial.LogOnThrow = False
			fiducial.RecoverLogged(path, date)
			if (type(fiducial) is ShapeModelFiducialFinder):
				fiducial.CircleFinder.InitShapeModel(fiducial.Cam)
			if (type(fiducial) is MorphologicalFiducialFinder):
				fiducial.CircleFinder.InitModel(fiducial)
			fiducial.AcquireFiducial(fiducial.LastImage)
			error = fiducial.FiducialPoseError
		except Exception, e: 
			message = e.Message
		finally:
			fiducial.CalibrationBounds = calBounds
			fiducial.LogOnThrow = True
			errorFiles.append((path + '\\' + name + '-' + date, error, message))
	return errorFiles

def SummaryError(errorFiles):
	maxError = 0
	failure = 0
	sumError = 0
	numError = 0
	for el in errorFiles:
		if (el[1] > 0):
			sumError += el[1]
			numError += 1
			if (el[1] > maxError):
				 maxError = el[1]
		else:
			failure +=1
	return [sumError/numError, maxError, numError, failure] 

def CollectRLData(shutterAdj, path):
	rls = [ '0', '0-1', '0-2', '0-3', '1', '1-1', '1-2', '1-3', '2', '2-1', '2-2', '2-3'] 
	rc.RaiseZ()
	oldPath = Imager.ImageLogDirStatic
	Imager.ImageLogDirStatic = path
	for suffix in rls:
		name = 'ReagentLoader-' + suffix;
		f = vt.Fiducials[name]
		oldCalibratedShutter = f.CalibratedShutter
		try :
			rc.MoveXYSafe(f.InitialImagingPos)
			f.CalibratedShutter = f.CalibratedShutter + shutterAdj
			f.Snap()
			f.LogCurrent()
		finally:	
			f.CalibratedShutter = oldCalibratedShutter 
	Imager.ImageLogDirStatic = oldPath

def ScanRL(shutters):
	rls = [ '0', '0-1', '0-2', '0-3', '1', '1-1', '1-2', '1-3', '2', '2-1', '2-2', '2-3'] 
	rc.RaiseZ()
	oCalShutters = {}
	r.NoScanInventory = True
	r.NoToolCalibration = True
	for suffix in rls:
		name = 'ReagentLoader-' + suffix;
		f = vt.Fiducials[name]
		oCalShutters[name] = f.CalibratedShutter
	
	for shutter in shutters:
		for suffix in rls:
			name = 'ReagentLoader-' + suffix;
			f = vt.Fiducials[name]
			f.CalibratedShutter = oCalShutters[name] + shutter
		try:
			r.Scan()
		finally:
			for suffix in rls:
				name = 'ReagentLoader-' + suffix;
				f = vt.Fiducials[name]
				f.CalibratedShutter = oCalShutters[name]

# To use:
# RecordFiducials()
def RecordFiducials(path='/tmp/fiducials/', shutterAdjs = [.75, 1, 1.25], offsetLoc = True):
	for kvp in vt.Fiducials:
		f = kvp.Value
		offsets = ((0,0,0))
		if (offsetLoc == True): offsets = [( 0.000,  0.000), \
																			 (-0.001,  0.000), \
																			 (-0.001, -0.001), \
																			 ( 0.000, -0.001), \
																			 ( 0.001, -0.001), \
																			 ( 0.001,  0.000), \
																			 ( 0.001,  0.001), \
																			 ( 0.000,  0.001), \
																			 (-0.001,  0.001)]
		shutter = f.CalibratedShutter
		imagelogdir = f.ImageLogDirInstance
		try :
			for offset in offsets:
				for shutterAdj in shutterAdjs:
						rc.RaiseZ()
						f.ImagingOffset = offset
						rc.MoveXY(f.ImagingPos)
						f.CalibratedShutter = f.CalibratedShutter * shutterAdj
						f.ImageLogDirInstance = path
						f.Snap()
						f.LogCurrent()
		finally:
			f.CalibratedShutter = shutter
			f.ImagingOffset = (0,0,0)
			f.ImageLogDirInstance = imagelogdir

def MakeNewStageFinder(vt):
	leftImager = Imager()
	leftImager.Cam = vt.RealCamera(CameraNames.StageLeft)

	rightImager = Imager()
	rightImager.Cam = vt.RealCamera(CameraNames.StageRight)

	f = StereoStageFinder(leftImager, rightImager)
	f.DistanceThreshold = 0.00003

	# Configure all
	f.Configure(vt, "NewStageFiducial")
	f.Left.Configure(f, "NewStageFiducialLeft")
	f.Right.Configure(f, "NewStageFiducialRight")

	vt.StereoFinders["NewStageFiducial"] = f;
	return f;
	
# Create the stage cameras
# At some point, allow vision_springfield to simulate fake cameras by separating out 
# camera instantiation w/ camera initialization.
def MakeSimulationStageCameras(vt):
	# Set up left camera.
	# At some point, create function to dump relevant cameraparams & cameraPose with images so we don't have to enter this manually.	Simple load and dump functions would be very helpful.
	camL = HALCONCameraWrapper(SimMVCamera(HImage("C:\\data\\stagefiducial\\StageLeft.tif"), "a4701110a51a0"))
	camL.Configure(vt, CameraNames.StageLeft)
	camL.Cam.CameraParams = ( 0.018039361935937824, 2286.5062639812791, -134058226.79330313, 8246497414602.1748, -0.014321875347547971, 0.038289671626716079, 4.65E-06, 4.65E-06, 514.47076650448048, 391.43855749557241, int(1024), int(768) )
	camL.Cam.CameraPose = ( 0.078146877206586737, -0.00020334951714156074, 0.027296072118367081, 359.77345215923197, 322.00227157639569, 359.46091877736353, 'Rp+T', 'gba', 'point')
	vt.Cameras[CameraNames.StageLeft] = camL;

	# set up right camera 
	camR = HALCONCameraWrapper(SimMVCamera(HImage("C:\\data\\stagefiducial\\StageRight.tif"), "a4701110a51a1"))
	camR.Cam.CameraParams = ( 0.018075621002122965, 1483.65325349237, 5779858.0431651808, -40744654559.745224, 0.081413625468201176, -0.046685277930092209, 4.65E-06, 4.65E-06, 534.6102856467935, 392.81537152512385, int(1024), int(768) )
	camR.Cam.CameraPose = ( -0.078385607065991347, -0.0004262414876378922, 0.026600117374718259, 359.86633766826742, 37.998102168762593, 0.50710065303215468, "Rp+T", "gba", "point" )
	camR.Configure(vt, CameraNames.StageRight)
	vt.Cameras[CameraNames.StageRight] = camR;

def MakeSimulationZCamera(vt):
	camZ = HALCONCameraWrapper(SimMVCamera(HImage("C:\\data\\stagefiducial\\StageLeft.tif"), "a4701110a51a0"))
	camZ.Cam.CameraParams = ( 0.00946142597417346, 3533.6218327686229, -111500893.62372717, 12460761338459.873, -0.022262567878933995, 0.072467978581762127, 4.65E-06, 4.65E-06, 522.55068098793822, 406.30861068401646, int(1024), int(768)	)
	camZ.Cam.CameraPose = ( 0.0, 0.0, 0.08, 180.0, 0.0, 0.0, "Rp+T", "gba", "point" )
	camZ.Configure(vt, CameraNames.RobotZ)
	vt.Cameras[CameraNames.RobotZ] = camZ;

def MakeSim(vt, rc):
	Imager.ImageLogDirStatic = 'C:\\data\\homerstate\\101112_102722'
	LoadFiducialState(vt, rc, '101112_102722')

def TestCameraShutter(cam, shutters, repeat, outputPath):
	recShutter = []
	recMean = []
	origCalValue = cam.Shutter
	cam.Gain = 0
	try: 
		cam.Illuminator.Enabled = True
		for shutter in shutters:
			cam.Shutter = shutter
			for i in range(1, repeat): 
				recShutter.append(shutter)
				recMean.append(cam.MeanValueFromEntireScene(cam.Grab(True).HImage))
		output = MFile('shutter_mean', outputPath )
		output.addLine(recShutter)
		output.addLine(recMean)
		output.close()
	finally:
		cam.Shutter = origCalValue
		cam.Illuminator.Enabled = False

def TimeTest(imager, duration, interval):
	from datetime import datetime
	from datetime import timedelta
	start = datetime.now()
	vals = {}
	while duration > datetime.now() - start:
		intensity = imager.Cam.MeanValueFromEntireScene(imager.Snap())
		time = str(datetime.now() - start)
		vals[time] = intensity
		print time + ' ' + str(intensity)
		sleep(interval)
	return vals

# class to generate matlab/octave compatible matrices for easy
# processing.	uses RAII to create and close files. 
class MFile:
	output = ''
	def __init__(self, title, fileName):
		print 'creating matlab file:' + fileName
		self.output = file(fileName, "w")
		self.output.write(title + "= [ ...\n")
	def addLine(self, vector):
		self.output.write("\t")
		self.output.write(", ".join([str(val) for val in vector]))
		self.output.write(";\n")
		self.output.flush()
	def close(self):
		print 'writing out matlab file.'
		self.output.write("]\n")
		self.output.close()
