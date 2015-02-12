# Temporary home of calibration code

import System
from PacBio.Common.Numeric import *

from instrumentGlobals import *


def captureDarkFrames():
    """Close shutters/TI and tell Otto to store our special dark frames"""
    shutter1.IsOpen = False
    shutter2.IsOpen = False
    ti.Enabled = False
    

def calVOA(ipath):
    ipath.Laser.Brightness = 300
    ipath.Laser.Enabled = True
    ipath.Shutter.IsOpen = True
    ipath.VOA.CalibrateVOA(ipath.PSB)
    ipath.Shutter.BeginOpen(False)
    ipath.Laser.Enabled = False
    #not needed - CalibrateVOA does this 
    #ipath.VOA.UpdateRepository(DeclDataClassification.Any, True)

    
def calVOA1():
	calVOA(instrument.IlluminationPath[532])
    
        
def calVOA2():
	calVOA(instrument.IlluminationPath[642])

def calCommon():
    """Common init """
    # calVOA1()
    # calVOA2()
    

def calPSB1():
    #green
    calib1 = Array.CreateInstance(Point2D, 2)
    calib1[0] = Point2D(0.0, 0)
    calib1[1] = Point2D(0.2, 1.0)   #indicates that encoder val 0.2 correspondes to 1 watt
    psb1.CalibrationCurve = calib1
    psb1.UpdateRepository("CalibrationCurve")

def calPSB2():
    #red
    calib1 = Array.CreateInstance(Point2D, 2)
    calib1[0] = Point2D(0.0, 0)
    calib1[1] = Point2D(0.2, 1.0)   #indicates that encoder val 0.2 correspondes to 1 watt
    psb2.CalibrationCurve = calib1
    psb2.UpdateRepository("CalibrationCurve")


def calRelayAxis(relay):
	rlgAxis = relay.VectorAxis

	# Set safe limits that will apply to both Red and Green paths
	rlgAxis.MaxPosition = (1.2e-2, 0)
	rlgAxis.MinPosition = (0, -8.0e-3)

	rlgAxis.UpdateRepository("MaxPosition")
	rlgAxis.UpdateRepository("MinPosition")

def calRelayCommon():
	calRelayAxis(relay1)
	calRelayAxis(relay2)

	#Calibration curve is common to all instruments
	#Settings provided by Janice in bug 4718
	#green
	calib1 = System.Array.CreateInstance(Point2D, 2)
	calib1[0] = Point2D(.2413, 0)
	calib1[1] = Point2D(.2487, .00598)
	relay1.L1FocalCalibrationCurve = calib1

	calib2 = System.Array.CreateInstance(Point2D, 2)
	calib2[0] = Point2D(.2413, 0)
	calib2[1] = Point2D(.2487, -.00243)
	relay1.L2FocalCalibrationCurve = calib2

	relay1.UpdateRepository("L1FocalCalibrationCurve")
	relay1.UpdateRepository("L2FocalCalibrationCurve")

	#red 
	calib1 = System.Array.CreateInstance(Point2D, 2)
	calib1[0] = Point2D(.2413, 0)
	calib1[1] = Point2D(.2487, .00548)
	relay2.L1FocalCalibrationCurve = calib1

	calib2 = System.Array.CreateInstance(Point2D, 2)
	calib2[0] = Point2D(.2413, 0)
	calib2[1] = Point2D(.2487, -.00259)
	relay2.L2FocalCalibrationCurve = calib2

	relay2.UpdateRepository("L1FocalCalibrationCurve")
	relay2.UpdateRepository("L2FocalCalibrationCurve")

    



calSwaComment =  """ALL OFFSET DATA INCLUDES THE 180DEG FLIP BUT DOES NOT INCLUDE THE NOMINAL +/-PI/4.  UNIT IN RADIANS.
 
Serial Number
 Motor #1 Offset (rad)
 Motor #2 Offset (rad)
 
Green 001
 3.07179
 3.08919
 
Red 001
 3.10668
 3.10668
 
Green 002
 2.60059
 3.14159
 
Red 002
 3.14159
 3.14159
 
Green 003
 0.31420
 -2.84270
 
Red 003
 0.87440
 -3.04950
 
Green 004
 2.69200
 2.87000
 
Red 004
 2.79500
 2.80500
""" 

# Temporary code for calibrating ralph
def calRalph():
	"""I don't quite trust that the DB on ralph will get toasted, so a command might be handy to program it with all the serial #s"""
	print "TEMPORARY - DEPRECATE WHEN DATABASE DEPLOYMENT IS ROBUST"
	
	calCommon()
	
	# SWA SN #1 for green
	swa1.UpdateCalibrationDB(3.07179, 3.08919)
	# SWA SN #1 for red 
	swa2.UpdateCalibrationDB(3.10668, 3.10668)
	
	calRelayCommon()
	
	#Settings provided by Janice in bug 4718
	#green
	relay1.L1Offset = MM(4.93)
	relay1.L2Offset = MM(-3.19)
	relay1.UpdateRepository("L1Offset")
	relay1.UpdateRepository("L2Offset")
	
	#red 
	relay2.L1Offset = MM(3.19)
	relay2.L2Offset = MM(-4.34)
	relay2.UpdateRepository("L1Offset")
	relay2.UpdateRepository("L2Offset")
	
	calPSB1()
	calPSB2()
	print "Done with ralph cal - database updated"


# Temporary code for calibrating nelson
def calNelson():
	print "TEMPORARY - DEPRECATE WHEN DATABASE DEPLOYMENT IS ROBUST"
	
	calCommon()
	    
	# SWA SN #3 for green
	swa1.UpdateCalibrationDB(0.31420, -2.84270)  
	# SWA SN #2 for red 
	swa2.UpdateCalibrationDB(3.1415926, 3.1415926)

	calRelayCommon()
		
	#Settings provided by Janice in bug 4718
	#green
	relay1.L1Offset = MM(4.63)
	relay1.L2Offset = MM(-3.31)
	relay1.UpdateRepository("L1Offset")
	relay1.UpdateRepository("L2Offset")

	#red 
	relay2.L1Offset = MM(2.73)
	relay2.L2Offset = MM(-4.88)
	relay2.UpdateRepository("L1Offset")
	relay2.UpdateRepository("L2Offset")
	
	calPSB1()
	calPSB2()

	print "Done with Nelson cal - database updated"    
	

# Temporary code for calibrating Milhouse
def calMilhouse():
	print "TEMPORARY - DEPRECATE WHEN DATABASE DEPLOYMENT IS ROBUST"

	calCommon()
	    
	# SWA SN #2 for green
	swa1.UpdateCalibrationDB(2.60059, 3.14159)
	# SWA SN #3 for red
	swa2.UpdateCalibrationDB(0.87440, -3.04950) 

	calRelayCommon()

	ti.VectorAxis.MaxPosition = ( 1.515, )
	ti.VectorAxis.UpdateRepository(DeclDataClassification.Any, True)
	
	ti.UpdateRepository(DeclDataClassification.Any, True)
	#Settings provided by Janice in bug 4718
	#green
	relay1.L1Offset = MM(4.10)
	relay1.L2Offset = MM(-3.29)
	relay1.UpdateRepository("L1Offset")
	relay1.UpdateRepository("L2Offset")

	#red 
	relay2.L1Offset = MM(3.66)
	relay2.L2Offset = MM(-3.99)
	relay2.UpdateRepository("L1Offset")
	relay2.UpdateRepository("L2Offset")

	calPSB1()
	calPSB2()

	print "Done with Milhouse cal - database updated"
	
# Temporary code for calibrating Martin
def calMartin():
    print "TEMPORARY - DEPRECATE WHEN DATABASE DEPLOYMENT IS ROBUST"

    calCommon()
        
    # SWA SN #4 for gre
    swa1.UpdateCalibrationDB(2.692,2.87)
    # SWA SN #4 for red
    swa2.UpdateCalibrationDB(2.795,2.805) 

    calRelayCommon()

    """This needs to be updated for Martin, these are currently Milhouse's numbers"""
    #Settings provided by Janice in bug 4718
    #green
    relay1.L1Offset = MM(3.610)
    relay1.L2Offset = MM(-3.605)
    relay1.UpdateRepository("L1Offset")
    relay1.UpdateRepository("L2Offset")

    #red 
    relay2.L1Offset = MM(3.66)
    relay2.L2Offset = MM(-3.99)
    relay2.UpdateRepository("L1Offset")
    relay2.UpdateRepository("L2Offset")

    calPSB1()
    calPSB2()

    print "Done with Martin cal - database updated"

def calAdrian():
    print "TEMPORARY - DEPRECATE WHEN DATABASE DEPLOYMENT IS ROBUST"

    calCommon()
        
    # SWA SN #5 for gre
    swa1.UpdateCalibrationDB(4.611,4.48)
    # SWA SN #5 for red
    swa2.UpdateCalibrationDB(3.72,3.52) 
    print "Done with Adrian cal - database updated"
    #green
    relay1.L1Offset = MM(2573*1.524e-3)
    relay1.L2Offset = MM(-1225*1.524e-3)
    relay1.UpdateRepository("L1Offset")
    relay1.UpdateRepository("L2Offset")

    #red 
    relay2.L1Offset = MM(3220*1.524e-3)
    relay2.L2Offset = MM(-1125*1.524e-3)
    relay2.UpdateRepository("L1Offset")
    relay2.UpdateRepository("L2Offset")

# config Chip-Tip loader velocities and acceleration.
def config_ChipTipLoader():
	config_Loader(instrument.ChipsTipsDrawer.ChipTipAxisDrawer)
	print 'chips & tips loader configuration updated'

# config Reagents loader velocities and acceleration.
def config_ReagentLoader():
	config_Loader(instrument.TemplateReagentDrawer.ReagentsAxisDrawer)
	print 'reagents loader configuration updated'

def config_Loader(loader):
	loaderMinVelocity = AppSettings.Instance['LoaderMinVelocity']
	if loaderMinVelocity == None:
		loaderMinVelocity = 0.064
	loaderMaxVelocity = AppSettings.Instance['LoaderMaxVelocity']
	if loaderMaxVelocity == None:
		loaderMaxVelocity = 0.064
	loaderMaxAcceleration = AppSettings.Instance['LoaderMaxAcceleration']
	if loaderMaxAcceleration == None:
		loaderMaxAcceleration = 0.064
	loaderTolerance = AppSettings.Instance['LoaderTolerance']
	if loaderTolerance == None:
		loaderTolerance = 0.0625

	loaderMinVelocity = float(loaderMinVelocity)
	loaderMaxVelocity = float(loaderMaxVelocity)
	loaderMaxAcceleration = float(loaderMaxAcceleration)
	loaderTolerance = float(loaderTolerance)

	axis = loader.Axis.VectorAxis # operate on the vector axis
	actuator = axis.Actuator
	
	# Note, we're making the assumption here that the loader
	# is a 1-dimensional axis. It should be, but may not be.
	
	actuator.MinVelocity = (loaderMinVelocity,)
	actuator.MaxVelocity = (loaderMaxVelocity,)
	actuator.MaxAcceleration = (loaderMaxAcceleration,)
	actuator.Tolerance = (loaderTolerance,)
	actuator.EditDeclRepository.UpdateRepository(DeclDataClassification.Any)
