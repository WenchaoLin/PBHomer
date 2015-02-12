from PacBio.Instrument.Halcon import *
from PacBio.Instrument.Homer import *
from PacBio.Instrument.Vision import *
from PacBio.Common.Numeric import *
from PacBio.Instrument.Interfaces import *
from PacBio.Instrument.Interfaces.Fluidics import *
from PacBio.Instrument.Interfaces.Homer import *
from PacBio.Instrument.Interfaces.Movement import *
from PacBio.Instrument.Interfaces.Vision import *
from PacBio.Instrument.Interlock import *
from PacBio.Instrument.RT import *
from PacBio.Instrument.Loader import *
from PacBio.Instrument.Protocols import *
from System import *
from System.IO import *
from System.Xml.Serialization import XmlSerializer
from System.Reflection import Assembly
import copy
import time
import clr
import string
import sys
from HalconDotNet import *

i = InstrumentContext.Instrument
r = InstrumentContext.Instrument.Robot

if r is not None:
    rc = r.RControl
    xy = InstrumentContext.Instrument.Robot.XYAxes
    z = InstrumentContext.Instrument.Robot.ZAxes
    vt = InstrumentContext.Instrument.Robot.VisionTools
    robotplus = i.RobotPlus
    workdeck = i.Workdeck

try:
	global p0, p1, g0, g1, o, cam, rp1, rp2
	gp0 = i.Grippers.GetGripper(0)
	gp1 = i.Grippers.GetGripper(1)
	pp0 = i.Fluidics["pipette-a"]
	pp1 = i.Fluidics["pipette-b"]
	o = vt.Oracle
	cam = vt.RealCamera("ZCamera")
	rp1 = i.RobotPipettor1
	rp2 = i.RobotPipettor2
	p0 = vt.Tools["Pipette0"]
	p1 = vt.Tools["Pipette1"]
	g0 = vt.Tools["Gripper0"]
	g1 = vt.Tools["Gripper1"]
except:
	print "Vision tools not available."

try:
    gp0 = i.Grippers.GetGripper(0)
    gp1 = i.Grippers.GetGripper(1)
    pp0 = i.Fluidics["pipette-a"]
    pp1 = i.Fluidics["pipette-b"]
except:
    pass

def tname(tool):
  if tool == p0:
    return "Pipette0"
  elif tool == p1:
    return "Pipette1"
  elif tool == g0:
    return "Gripper0"
  elif tool == g1:
    return "Gripper1"
  else:
    return "bogus"

def tnum(tool):
  if tool == p0:
    return 0
  elif tool == p1:
    return 2
  elif tool == g0:
    return 1
  elif tool == g1:
    return 3
  else:
    return "bogus"

def gripper(tool):
  if tool == g0:
    return gp0
  elif tool == g1:
    return gp1
  else:
    return "bogus"

def pipette(tool):
  if tool == p0:
    return pp0
  elif tool == p1:
    return pp1
  else:
    return "bogus"

def turnOn():
  InterlockManager.Instance.ClearEmergencyStop()
  InterlockManager.Instance.ClearRobotInterlock()
  xy.Controller.DrivesOn()

def drivesOn():
  xy.Controller.DrivesOn()

def drivesOff():
  xy.Controller.DrivesOff()

def goOffset(tool, pname, offset):
  rc.RaiseZ()
  pn = tname(tool) + "-" + pname
  p = o.GetPosition(pn)
  print pn + ": " + str(p)
  rc.MoveXY(p)
  rc.MoveZOffset(p, tnum(tool), offset)

def pickupTip(p, box, pos):
  r.PickupPipetteTip(p, InstrumentLocation("TipBox-" + str(box) + "-" + pos))

def ejectTip(p):
  r.DisposePipetteTip(p)

def goWell(pos):
  robot.MovePipetteToWell(Pipette.Pipette1, InstrumentLocation("ReagentPlate-0-" + pos))

def chuckTips():
  for row in range(0, 15):
    for col in range(0, 24):
      pos = MVLocationName.ShortPlateWellName(row, col)
      pickupTip(pos)
      ejectTip()

def goPosition(name):
  if pz != None:
    pz.TargetPosition = 0
    pz.WaitForMove()
  
  pn = "Pipette0-" + name
  p = o.GetPosition(pn)
  print pn + ": " + str(p)
  xy.TargetPosition = (p[0], p[1])
  xy.WaitForMove()
  if pz != None:
    pz.TargetPosition = p[2] - 0.001
    pz.WaitForMove()

def pickupLid(g, num):
  r.PickupChipLid(g, InstrumentLocation("ChipPrep-" + str(num)))

def dropLid(g, num):
  r.PlaceChipLid(g, InstrumentLocation("ChipPrep-" + str(num)))

def wiggleChip(p, tip, station):
  pickupTip(p, tip)
  cpsl = InstrumentLocation("ChipPrep-" + str(station))
  r.MovePipetteToWellXYPosition(p, cpsl, XYRobotSpeed.High)
  r.MovePipetteToChipZPosition(p, cpsl, ChipZPosition.ChipBottomPosition, ZRobotSpeed.High)
  r.MovePipetteToChipAspiratePosition(p, cpsl)
  #ejectTip(p)

def shuffleLids():
  for i in range(0, 12):
    pickupLid(Gripper.Gripper1, i)
    dropLid(Gripper.Gripper1, i+3)
  
  for i in range(0, 12):
    pickupLid(Gripper.Gripper1, 14-i)
    dropLid(Gripper.Gripper1, 11-i)

def breakChip(g, strip, chip):
  r.BreakOutChip(g, InstrumentLocation("ChipStrip-" + str(strip) + "-" + str(chip)))

def pipetteIdealCalib(pip, liquid, steps, ul):
  """
  Calibrate a pipette with an ideal calibration curve.

  p -- the pipette to calibrate (must be p0 or p1).
  liquid -- the liquid class to calibrate for (e.g., Aqueous)
  steps -- the number of steps that correspond to the given volume
  ul -- the liquid volume, in uL.
  """
  calib = PipetteCalibrationInfo()
  calib.LiquidClass = liquid
  calib.AspiratePoints = (Point2D(0, 0), Point2D(Units.UL(ul), steps))
  calib.DispensePoints = (Point2D(0, 0), Point2D(Units.UL(ul), -steps))
  pip[liquid] = calib

def pipetteLoadCalib(p, liquid, path):
  """
  Load a pipette calibration file for the given liquid class, calibrating
  the pipette p.

  p must be one of the pipettor tools -- p0 or p1.
  """
  serial = XmlSerializer(PipetteCalibrationInfo)
  stream = FileStream(path, FileMode.Open, FileAccess.Read)
  try:
    calib = serial.Deserialize(stream)
    p[liquid] = calib
  finally:
    stream.Close()

def aspirate(p, liquid, vol):
  """
  Aspriate the given volume, in uL, using the specified pipette p.

  p must be one of the pipettor tools -- p0 or p1.
  """
  pip = pipette(p)
  pip.FluidicsTag = liquid
  return pip.Aspirate(Units.UL(vol))

def dispense(p, liquid, vol):
  """
  Dispense the given volume, in uL, using the specified pipette p.

  p must be one of the pipettor tools -- p0 or p1.
  """
  pip = pipette(p)
  pip.FluidicsTag = liquid
  return pip.Dispense(Units.UL(vol))

# robot.PickupPipetteTip(Pipette.Pipette1, InstrumentLocation("TipBox-0-A01", Point2D(0, 0)))
# robot.DisposePipetteTip(Pipette.Pipette1)
# xy.TargetPosition = (-0.5098, -0.0283)
# pz.TargetPosition = 0.12
# vt.Tools["Pipette0"].AcquireFiducial()
# cam.HCameraPose = cam.HCameraPose.PoseToHomMat3d().HomMat3dInvert().HomMat3dToPose()

#inventory debugging
def haveTipScanners():
  return vt.Fiducials.ContainsKey('TipNest-0')

def haveChipScanners():
  return vt.Fiducials.ContainsKey('ChipTray-0')

def haveReagentScanner():
  return vt.Fiducials.ContainsKey('ReagentLoader-0')

def haveAllInventoryScanners():
  return haveTipScanners() and haveChipScanners() and haveReagentScanner()

def tipScanNum():
  if (haveAllInventoryScanners()):
    return 4
  elif(not haveTipScanners()):
    return -1
  elif(haveTipScanners() and haveChipScanners()):
    return 3
  elif(haveTipScanners() and haveReagentScanner()):
    return 1
  else:
    return 0
    
def chipScanNum():
  if(not haveChipScanners()):
    return -1
  elif(haveReagentScanner()):
    return 1
  else:
    return 0

def saveTipImages(runid):
  for i in range(tipScanNum(), tipScanNum()+6):
    for j in range(0,4):
      r.InventoryScanner.Scanners[i].RegionFinders[j].WriteLastImage("/tmp/"+runid+"Tip"+str(i)+"Box"+str(j)+".tiff")

def saveChipImages(runid):
  for i in range(chipScanNum(), chipScanNum()+3):
    for j in range(0,4):
      r.InventoryScanner.Scanners[i].RegionFinders[j].WriteLastImage("/tmp/"+runid+"Chip"+str(i)+"Strip"+str(j)+".tiff")

def changeTipShutter(speed):
  for i in range(tipScanNum(), tipScanNum()+6):
    for j in range(0,4):
      r.InventoryScanner.Scanners[i].RegionFinders[j].Shutter = speed

def changeChipShutter(speed):
  for i in range(chipScanNum(), chipScanNum()+3):
    for j in range(0,4):
      r.InventoryScanner.Scanners[i].RegionFinders[j].Shutter = speed

def changeTipDebug(value):
  for i in range(tipScanNum(), tipScanNum()+6):
    r.InventoryScanner.Scanners[i].DebugFlag = value

def backgroundMaxEdgeArea(value):
  for i in range(0, tipScanNum()+6):
    r.InventoryScanner.Scanners[i].backgroundEdgeMax = value

#Expects to be given 0-5
def oneBoxInventory(i):
  sumdata = 0
  for j in range(0, 16):
    for k in range(0, 24):
      if (InstrumentContext.Instrument.ChipsTipsDrawer.PipetteTipTray.TipBoxes[i].Present[j,k]):
        sumdata=sumdata+1
  return sumdata

def saveTipInventory(runid):
  f= open('/tmp/'+runid+'.txt', 'w')
  for i in range(tipScanNum(), tipScanNum()+6):
    sum = oneBoxInventory(i-tipScanNum())
    f.write(sum.ToString())
    f.write(' ')
  f.close()

def chipBarcodeResults():
  retval=""
  failures=0
  for i in range(chipScanNum(), chipScanNum()+3):
    for j in range(0,4):
      if(r.InventoryScanner.Scanners[i].Barcodes.ContainsKey("ChipStrip-"+(4*(i-chipScanNum())+j).ToString())):
        retval = retval + "1 "
      else:
        retval = retval + "0 "
        failures += 1
  return retval,failures

def fullChipBarcodeResults():
  retval=""
  for i in range(chipScanNum(),chipScanNum()+3):
    for j in range(0,4):
      if(r.InventoryScanner.Scanners[i].Barcodes.ContainsKey("ChipStrip-"+(4*(i-chipScanNum())+j).ToString())):
        retval = retval + "{"+r.InventoryScanner.Scanners[i].Barcodes["ChipStrip-"+(4*(i-chipScanNum())+j).ToString()].Text + "} "
      else:
        retval = retval + "0 "
  return retval

def disableSerialTip():
  for i in range(tipScanNum(), tipScanNum()+6):
    r.InventoryScanner.Scanners[i].serialUseOnly = False

def enableSerialTip():
  for i in range(tipScanNum(), tipScanNum()+6):
    r.InventoryScanner.Scanners[i].serialUseOnly = True

from vision_springfield import MakeSWATJigFiducial
def enableSWATJig():
  if i.ChipsTipsDrawer.GetManualBarcode("TestJig") is None:
    i.ChipsTipsDrawer.SetManualBarcode("TestJig", "unknown")
  if HalconUtil.IsHalconAvailable and \
    (not vt.Fiducials.ContainsKey("SWATJig")):
    MakeSWATJigFiducial(vt)
    if (tipScanNum() >= 0):
      r.InventoryScanner.Scanners[tipScanNum()+4].InUse = False

def disableSWATJig():
  i.ChipsTipsDrawer.ClearManualBarcode("TestJig")
  if vt.Fiducials.ContainsKey("SWATJig"):
    f = vt.Fiducials["SWATJig"]
    f.Parent.RemoveChild(f)
    vt.Fiducials.Remove("SWATJig")
    if (tipScanNum() >= 0):
      r.InventoryScanner.Scanners[tipScanNum()+4].InUse = True

def isSWATJigEnabled():
  return (i.ChipsTipsDrawer.GetManualBarcode("TestJig") is not None) or vt.Fiducials.ContainsKey("SWATJig")

from vision_springfield import MakeMVSPlate,RemoveMVSPlate
def enableMVS(loc=4, wells=96):
  if wells!=96 and wells!=384:
      print "Supported MVS well sizes: 96 & 384."
      return
  if MakeMVSPlate(vt, r, loc, wells):
      r.InventoryScanner.Scanners[tipScanNum()+loc].InUse = False
  else:
      print "Error in creating an MVS plate with "+str(wells)+" wells at location "+str(loc)+"."

def disableMVS(loc=4):
  RemoveMVSPlate(vt, loc)
  r.InventoryScanner.Scanners[tipScanNum()+loc].InUse = True

from vision_springfield import MakeMagBeadLoader
def enableMagBead():
  if vt.Fiducials.ContainsKey("MagBead-0") and vt.Fiducials.ContainsKey("MagBead-1"):
    print "MagBead already enabled."
    return
  #if we only have one or the other, remove it to clear the way for a clean creation
  elif vt.Fiducials.ContainsKey("MagBead-0"):
    f = vt.Fiducials["MagBead-0"]
    f.Parent.RemoveChild(f)
    vt.Fiducials.Remove("MagBead-0")
  elif vt.Fiducials.ContainsKey("MagBead-1"):
    f = vt.Fiducials["MagBead-1"]
    f.Parent.RemoveChild(f)
    vt.Fiducials.Remove("MagBead-1")
  MakeMagBeadLoader(vt, r.XYAxes)
  InstrumentContext.Instrument.ChipPrepStationController.MagBeadController.Present=True

def disableMagBead():
  InstrumentContext.Instrument.ChipPrepStationController.MagBeadController.Present=False
  if vt.Fiducials.ContainsKey("MagBead-0"):
    f = vt.Fiducials["MagBead-0"]
    f.Parent.RemoveChild(f)
    vt.Fiducials.Remove("MagBead-0")
  if vt.Fiducials.ContainsKey("MagBead-1"):
    f = vt.Fiducials["MagBead-1"]
    f.Parent.RemoveChild(f)
    vt.Fiducials.Remove("MagBead-1")

from PacBio.Instrument.Robot import ChipStripScanner
def enableChipTray():
	for f in vt.Fiducials:
		if f.Key.startswith('ChipTray'):
			f.Value.Enabled = True
	
	for s in r.InventoryScanner.Scanners:
		if type(s) is ChipStripScanner:
			s.Enabled = True

def disableChipTray():
	for f in vt.Fiducials:
		if f.Key.startswith('ChipTray'):
			f.Value.Enabled = False
	
	for s in r.InventoryScanner.Scanners:
		if type(s) is ChipStripScanner:
			s.Enabled = False

def calibrateWell(pipette, well):
  tipLoc = InstrumentContext.Instrument.ChipsTipsDrawer.PipetteTipTray.GetNextTipWell(pipette)
  wm = WellZMap.Instance
  loc = InstrumentLocation(well)
  nominal = wm.ZOffset(well, WellZPosition.WellBottomNominalPosition)
  r.PickupPipetteTip(pipette, tipLoc)
  r.CalibrateTipLoading(pipette)
  r.MovePipetteToWell(pipette, loc, 0.0)
  r.ZSpeed = ZRobotSpeed.LowSeptaSpeed
  r.CalibrateWellDepth(pipette, loc, nominal)
  r.MovePipetteToWellZPosition(pipette, loc, 0.0)
  r.ZSpeed = ZRobotSpeed.High
  r.DisposePipetteTip(pipette)

def calCorners(pipette):
  calibrateWell(pipette, MVLocationName.ReagentPlate0 + "-A01")
  calibrateWell(pipette, MVLocationName.ReagentPlate0 + "-A12")
  calibrateWell(pipette, MVLocationName.ReagentPlate0 + "-H01")
  calibrateWell(pipette, MVLocationName.ReagentPlate0 + "-H12")
  calibrateWell(pipette, MVLocationName.ReagentPlate1 + "-A01")
  calibrateWell(pipette, MVLocationName.ReagentPlate1 + "-A12")
  calibrateWell(pipette, MVLocationName.ReagentPlate1 + "-H01")
  calibrateWell(pipette, MVLocationName.ReagentPlate1 + "-H12")
  calibrateWell(pipette, MVLocationName.SamplePlate + "-A01")
  calibrateWell(pipette, MVLocationName.SamplePlate + "-A12")
  calibrateWell(pipette, MVLocationName.SamplePlate + "-H01")
  calibrateWell(pipette, MVLocationName.SamplePlate + "-H12")
  calibrateWell(pipette, MVLocationName.MixingPlate + "-A01")
  calibrateWell(pipette, MVLocationName.MixingPlate + "-A24")
  calibrateWell(pipette, MVLocationName.MixingPlate + "-P01")
  calibrateWell(pipette, MVLocationName.MixingPlate + "-P24")

def interpolate96Well(plateName, pipetteName):
  q0 = o.GetPosition(pipetteName + "-" + plateName + "-A01")
  q1 = o.GetPosition(pipetteName + "-" + plateName + "-A12")
  q2 = o.GetPosition(pipetteName + "-" + plateName + "-H01")
  q3 = o.GetPosition(pipetteName + "-" + plateName + "-H12")
  p0 = Point2D(0, 0)
  p1 = Point2D(0.099, 0.063)
  inter = InterpolateFourPoints((q0, q1, q2, q3), p0, p1)
  for i in range(0, 12):
    for j in range(0, 8):
      pos = inter.Interpolate(Point2D(i*0.009, j*0.009))
      pname = pipetteName + "-" + plateName + "-" + MVLocationName.ShortPlateWellName(j, i)
      print "pname: " + pname + ", pos: " + str(pos)
      o.CalibratePosition(pname, pos)

def interpolate384Well(plateName, pipetteName):
  q0 = o.GetPosition(pipetteName + "-" + plateName + "-A01")
  q1 = o.GetPosition(pipetteName + "-" + plateName + "-A24")
  q2 = o.GetPosition(pipetteName + "-" + plateName + "-P01")
  q3 = o.GetPosition(pipetteName + "-" + plateName + "-P24")
  p0 = Point2D(0, 0)
  p1 = Point2D(0.1035, 0.0675)
  inter = InterpolateFourPoints((q0, q1, q2, q3), p0, p1)
  for i in range(0, 24):
    for j in range(0, 16):
      pos = inter.Interpolate(Point2D(i*0.0045, j*0.0045))
      pname = pipetteName + "-" + plateName + "-" + MVLocationName.ShortPlateWellName(j, i)
      print "pname: " + pname + ", pos: " + str(pos)
      o.CalibratePosition(pname, pos)

def interpolateRLDepthFromCalibration():
  interpolate96Well(MVLocationName.ReagentPlate0, MVLocationName.Pipette0)
  interpolate96Well(MVLocationName.ReagentPlate0, MVLocationName.Pipette1)
  interpolate96Well(MVLocationName.ReagentPlate1, MVLocationName.Pipette0)
  interpolate96Well(MVLocationName.ReagentPlate1, MVLocationName.Pipette1)
  interpolate96Well(MVLocationName.SamplePlate, MVLocationName.Pipette0)
  interpolate96Well(MVLocationName.SamplePlate, MVLocationName.Pipette1)
  interpolate384Well(MVLocationName.MixingPlate, MVLocationName.Pipette0)
  interpolate384Well(MVLocationName.MixingPlate, MVLocationName.Pipette1)


def MakeFCRChimneyFiducialLocator(vt):
  leftImager = Imager()
  leftImager.Cam = vt.RealCamera(CameraNames.StageLeft)
  
  rightImager = Imager()
  rightImager.Cam = vt.RealCamera(CameraNames.StageRight)
  
  f = StereoStageFinder(leftImager, rightImager)
  f.DistanceThreshold = 0.00003
  
  f.PoseTarget = HaveCameraPose() 
  
  # set up the specialized finders
  # will probably need something a bit more robust.
  f.LeftFinder.PolyFinder.NumResults = 3
  f.LeftFinder.UseImagePoint = lambda rs, cs : (rs[1], cs[1])
  f.RightFinder.PolyFinder.NumResults = 1
  f.RightFinder.UseImagePoint = lambda rs, cs : (rs[0], cs[0])
   
  f.Configure(vt, "ChimneyFiducial")
  f.Left.Configure(f, "ChimneyFiducialLeft")
  f.Right.Configure(f, "ChimneyFiducialRight")
  vt.StereoFinders["ChimneyFiducial"] = f
  
  return f;

# Call MakeFCRChimneyFiducialLocator(vt) first.
def findStageOffset():
  csf = vt.StereoFinders['ChimneyFiducial']
  ssf = vt.StereoFinders['StageFiducial']

  # snap and acquire (but don't try to find the pose)
  csf.Snap()
  csf.AcquireFromImages()
  pt = csf.ObjectPositionRight
  
  # transform the point based on the pose from the stereo stage finder
  tr = ssf.PoseTarget.HCameraPose.PoseToHomMat3d().HomMat3dInvert()
  pt_camSpace = tr.AffineTransPoint3d(pt[0], pt[1], pt[2])
  
  # find the offset, need to add the virtual sharp as well.
  tipToBot = 0.04
  cadOffset = [-0.0225, 0.0115, 0.03193 + 0.000125]
  # remember, the system uses a left hand coordinate system while the camera
  # uses a positive one.  That's why the pt_camSpace[2] is flipped.
  stageOffset = [pt_camSpace[0] - cadOffset[0], \
                 pt_camSpace[1] - cadOffset[1], \
                 tipToBot - pt_camSpace[2] - cadOffset[2]]

  return (pt_camSpace, stageOffset)

# Run InventoryScan first
def calibrateRLDepth():
  calCorners(Pipette.Pipette1)
  calCorners(Pipette.Pipette2)
  interpolateRLDepthFromCalibration()

def tipInv(tb):
  inv = InstrumentContext.Instrument.ChipsTipsDrawer.PipetteTipTray.TipBoxes[tb].Present
  for j in range(16):
    line = ''
    if j==8:
      print '-------------------------------------------------'
    for k in range(24):
      if inv[j,k]:
        line+='o '
      else:
        line +='x '
      if k==11:
        line += '| '
    print line

def saveTipDebugImages(runid='Default'):
  saveTipImages(runid)
  #save the specific info for each box
  f = open('/tmp/'+runid+'TipInfo.txt','w')
  f.write(str(r.InventoryScanner.Scanners[4].RegionFinders[0].Cam.CameraPose)+'\r\n')
  f.write(str(r.InventoryScanner.Scanners[4].RegionFinders[0].Cam.CameraParams)+'\r\n')
  for tipBox in range(4,10):
    f.write(oneBoxInvStr(tipBox))
  f.close()

def oneBoxInvStr(whichBox=4):
  retval = ''
  for rf in range(0,4):
    for j in range(1,97):
      mrf = r.InventoryScanner.Scanners[whichBox].RegionFinders[rf]
      (row,col) = prfFind(mrf.LastImage, mrf, j)
      retval += str(whichBox)+' '+str(rf)+' '+str(j)+' '+row.ToString()+' '+col.ToString()+'\r\n'
  return retval

def prfFind(im, imager,counter):
  xp = imager.Regions[counter].XPoints
  yp = imager.Regions[counter].YPoints
  zp = imager.Regions[counter].ZPoints
  fiducial = imager.Fiducial
  imagingPos = imager.ImagingPos
  moveX = imagingPos[0]-fiducial.ImagingPos[0]
  moveY = imagingPos[1]-fiducial.ImagingPos[1]
  rOrigin = fiducial.MPlaneToRobot(Array.CreateInstance(float,3))
  rOrigin[0] = rOrigin[0]+moveX
  rOrigin[1] = rOrigin[1]+moveY
  newOrigin = fiducial.RobotToMPlane(rOrigin)
  newCameraPose = fiducial.HFiducialPose.SetOriginPose(newOrigin[0], newOrigin[1], newOrigin[2])
  (tx,ty,tz) = newCameraPose.PoseToHomMat3d().AffineTransPoint3d(HTuple(xp), HTuple(yp), HTuple(zp))
  (row, column) = HMisc.Project3dPoint(tx, ty, tz, imager.Cam.HCameraParams)
  return (row, column)

# Used to print out all fiducial errors
def printFiducialErrors():
  for kvp in vt.Fiducials:
    print kvp.Key + " " + str(kvp.Value.FiducialPoseError) + " " + str(kvp.Value.CalibrationBounds)

# Used to check the performance of one fiducial.
# Will command robot to location to take new image to process.
def checkFiducial(name):
  f = vt.Fiducials[name]
  ob = f.CalibrationBounds
  try: 
    f.CalibrationBounds = 1
    rc.RaiseZ()
    rc.MoveXY(f.InitialImagingPos)
    f.AcquireFiducial(f.Snap())
    print 'Error: ' + str(f.FiducialPoseError)
  finally:
    f.CalibrationBounds = ob

