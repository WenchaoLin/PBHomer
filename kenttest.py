from robotics import *
from PacBio.Instrument.Robot import *
from PacBio.Instrument.Vision import *
from PacBio.Instrument.Loader import *
from PacBio.Instrument.Protocols import *
from PacBio.Common.Numeric import *
from System.Collections.Generic import *

########################################
# Test force sensor.

def touchTest(idx, thresh):
    rc.SetZSpeed(ZRobotSpeed.High)
    rc.RaiseZ()
    rc.SetZSpeed(ZRobotSpeed.TouchForce)
    rc.TouchZOffset(idx, 0.02, thresh)

########################################
# Chip breakout test functions.

def printStats():
  print "Foil pos:   " + str(r.DepackageChip.LastFoilPosition)
  print "Chip pos:   " + str(r.DepackageChip.LastChipPosition)
  print "Bottom pos: " + str(r.DepackageChip.LastBottomPosition)

def breakStrip(strip):
    r.DepackageChip.EnableDiags = True
    for i in range (0,4):
        r.BreakOutChip(Gripper.Gripper1, InstrumentLocation("ChipStrip-" + str(strip) + "-" + str(2*i)))
        printStats()
        r.BreakOutChip(Gripper.Gripper2, InstrumentLocation("ChipStrip-" + str(strip) + "-" + str(2*i+1)))
        printStats()
        r.DisposeChip(Gripper.Both)

def breakTray():
  for i in range(0, 12):
    breakStrip(i)

######################################
# Well depth calibration testing (test jig, etc)
def calibrateOne(num):
  r.CalibrateTipLoading(Pipette.Pipette2)
  r.MovePipetteToWellXYPosition(Pipette.Pipette2, InstrumentLocation("TestJigChip-"+str(num)))
  r.CalibrateWellDepth(Pipette.Pipette2, InstrumentLocation("TestJigChip-"+str(num)), 0.0059)
  rc.RaiseZ()

def testOne(num):
  r.CalibrateTipLoading(Pipette.Pipette2)
  r.MovePipetteToChipXYPosition(Pipette.Pipette2, InstrumentLocation("TestJigChip-"+str(num)))
  r.MovePipetteToChipZPosition(Pipette.Pipette2, InstrumentLocation("TestJigChip-"+str(num)), ChipZPosition.ChipBottomPosition)
  r.MovePipetteToChipAspiratePosition(Pipette.Pipette2, InstrumentLocation("TestJigChip-"+str(num)))

def calibrateWells():
  for i in range(0, 6):
    r.CalibrateTipLoading(Pipette.Pipette2)
    r.MovePipetteToWellXYPosition(Pipette.Pipette2, InstrumentLocation("TestJigChip-"+str(i)))
    r.CalibrateWellDepth(Pipette.Pipette2, InstrumentLocation("TestJigChip-"+str(i)), 0.0059)

def calibrateCPS():
  for i in range(1, 10):
	r.CalibrateTipLoading(Pipette.Pipette2)
	r.PickupChipLid(Gripper.Gripper1, InstrumentLocation("ChipPrep-"+str(i)))
	r.CalibrateWellDepth(Pipette.Pipette2, InstrumentLocation("ChipPrep-"+str(i)), 0.0059)
	r.PlaceChipLid(Gripper.Gripper1, InstrumentLocation("ChipPrep-"+str(i)))

def wiggleChips():
  r.CalibrateTipLoading(Pipette.Pipette2)
  for i in range(0, 6):
  	r.MovePipetteToChipXYPosition(Pipette.Pipette2, InstrumentLocation("TestJigChip-"+str(i)))
  	r.MovePipetteToChipZPosition(Pipette.Pipette2, InstrumentLocation("TestJigChip-"+str(i)), ChipZPosition.ChipBottomPosition)
  	r.MovePipetteToChipAspiratePosition(Pipette.Pipette2, InstrumentLocation("TestJigChip-"+str(i)))

#########################################
# Tip loading tests.
def zPad(num):
  if num < 10:
    return "0" + str(num)
  else:
    return str(num)

def tipCalTest():
  for k in range(2, 3):
    for i in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P'):
      for j in range(0, 24):
        r.PickupPipetteTip(Pipette.Pipette2, InstrumentLocation("TipBox-" + str(2*k) + "-" + i + zPad(j+1)))
        r.PickupPipetteTip(Pipette.Pipette1, InstrumentLocation("TipBox-" + str(2*k+1) + "-" + i + zPad(j+1)))
        r.CalibrateTipLoading(Pipette.Pipette1)
        r.CalibrateTipLoading(Pipette.Pipette2)
        r.DisposePipetteTip(Pipette.Both)


def tipEjectTest(iter):
  for i in range(0, iter):
    print "************************* Test iteration " + str(i)
    r.DisposePipetteTip(Pipette.Both)

#################################################
# Chip pickup tests (jig)
def pickupTestCycle():
  r.PickupChip(Gripper.Gripper1, InstrumentLocation("TestJigChip-0"))
  r.PlaceChip(Gripper.Gripper1, InstrumentLocation("TestJigChip-1"))
  r.PickupChip(Gripper.Gripper2, InstrumentLocation("TestJigChip-1"))
  r.PlaceChip(Gripper.Gripper2, InstrumentLocation("TestJigChip-2"))
  r.PickupChip(Gripper.Gripper1, InstrumentLocation("TestJigChip-2"))
  r.PlaceChip(Gripper.Gripper1, InstrumentLocation("TestJigChip-3"))
  r.PickupChip(Gripper.Gripper2, InstrumentLocation("TestJigChip-3"))
  r.PlaceChip(Gripper.Gripper2, InstrumentLocation("TestJigChip-4"))
  r.PickupChip(Gripper.Gripper1, InstrumentLocation("TestJigChip-4"))
  r.PlaceChip(Gripper.Gripper1, InstrumentLocation("TestJigChip-5"))
  r.PickupChip(Gripper.Gripper2, InstrumentLocation("TestJigChip-5"))
  r.PlaceChip(Gripper.Gripper2, InstrumentLocation("TestJigChip-0"))

def pickupTest(iter):
  for i in range(0, iter):
    print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& Test cycle: " + str(i)
    pickupTestCycle()

def pickupTestSeq(gripper):
  r.PickupChip(gripper, InstrumentLocation("TestJigChip-0"))
  r.PlaceChip(gripper, InstrumentLocation("TestJigChip-1"))
  r.PickupChip(gripper, InstrumentLocation("TestJigChip-1"))
  r.PlaceChip(gripper, InstrumentLocation("TestJigChip-2"))
  r.PickupChip(gripper, InstrumentLocation("TestJigChip-2"))
  r.PlaceChip(gripper, InstrumentLocation("TestJigChip-3"))
  r.PickupChip(gripper, InstrumentLocation("TestJigChip-3"))
  r.PlaceChip(gripper, InstrumentLocation("TestJigChip-4"))
  r.PickupChip(gripper, InstrumentLocation("TestJigChip-4"))
  r.PlaceChip(gripper, InstrumentLocation("TestJigChip-5"))
  r.PickupChip(gripper, InstrumentLocation("TestJigChip-5"))
  r.PlaceChip(gripper, InstrumentLocation("TestJigChip-0"))

#################
# Lid pickup/place test

def lidTestR(iter):
  for i in range(0, iter):
    print "****************** Test iteration " + str(i)
    r.PickupChipLid(Gripper.Gripper1, InstrumentLocation("ChipPrep-0"))
    r.PlaceChipLid(Gripper.Gripper1, InstrumentLocation("ChipPrep-0"))
    r.PickupChipLid(Gripper.Gripper2, InstrumentLocation("ChipPrep-1"))
    r.PlaceChipLid(Gripper.Gripper2, InstrumentLocation("ChipPrep-1"))

def lidTestOne(pos):
  l1 = str(2*pos)
  l2 = str(2*pos+1)
  r.PickupChipLid(Gripper.Gripper1, InstrumentLocation("ChipPrep-" + l1))
  r.PickupChipLid(Gripper.Gripper2, InstrumentLocation("ChipPrep-" + l2))
  r.PlaceChipLid(Gripper.Gripper1, InstrumentLocation("ChipPrep-" + l2))
  r.PlaceChipLid(Gripper.Gripper2, InstrumentLocation("ChipPrep-" + l1))

def lidTest(iter):
  for i in range(0, iter):
    for j in range(0, 4):
      print "****************** Test iteration " + str(4*i + j)
      lidTestOne(j)

def chipTestOne(pos):
  l1 = str(2*pos)
  l2 = str(2*pos+1)
  r.PickupChip(Gripper.Gripper1, InstrumentLocation("ChipPrep-" + l1))
  r.PickupChip(Gripper.Gripper2, InstrumentLocation("ChipPrep-" + l2))
  r.PlaceChip(Gripper.Gripper1, InstrumentLocation("ChipPrep-" + l2))
  r.PlaceChip(Gripper.Gripper2, InstrumentLocation("ChipPrep-" + l1))

def chipTest(iter):
  for i in range(0, iter):
    for j in range(0, 4):
      print "****************** Test iteration " + str(4*i + j)
      chipTestOne(j)

def cleanStation(pos, drop):
  r.PickupChipLid(Gripper.Gripper1, InstrumentLocation("ChipPrep-" + str(pos)))
  r.PickupChip(Gripper.Gripper2, InstrumentLocation("ChipPrep-" + str(pos)))
  r.PlaceChipLid(Gripper.Gripper1, InstrumentLocation("ChipPrep-" + str(pos)))
  r.PlaceChip(Gripper.Gripper2, InstrumentLocation("TestJigChip-" + str(drop)))

def fillStation(cps, chip):
  r.BreakOutChip(Gripper.Gripper2, InstrumentLocation("ChipStrip-0-" + str(chip)))
  r.PickupChipLid(Gripper.Gripper1, InstrumentLocation("ChipPrep-" + str(cps)))
  r.PlaceChip(Gripper.Gripper2, InstrumentLocation("ChipPrep-" + str(cps)))
  r.PlaceChipLid(Gripper.Gripper1, InstrumentLocation("ChipPrep-" + str(cps)))

def testNoChip(cps, pickupG, probeG):
  loc = InstrumentLocation("ChipPrep-" + str(cps))
  r.PickupChip(pickupG, loc)
  try:
    r.PickupChip(probeG, loc)
  except:
    print "$$$$$$$$$$$$$$$$$$$$ pickup threw exception"
    r.PlaceChip(pickupG, loc)
    return
  
  r.PlaceChip(pickupG, loc)
  raise Exception("False positive on chip")

def testNoChipAll():
  for i in range(0, 8):
    testNoChip(i, Gripper.Gripper1, Gripper.Gripper2)
    testNoChip(i, Gripper.Gripper2, Gripper.Gripper1)

def testStation(cps, lidG, chipG, pipette):
  loc = InstrumentLocation("ChipPrep-" + str(cps))
  r.PickupChipLid(lidG, loc)
  r.PickupChip(chipG, loc)
  r.PlaceChip(chipG, loc)
  #r.MovePipetteToChipXYPosition(pipette, loc)
  #r.MovePipetteToChipZPosition(pipette, loc, ChipZPosition.ChipTopPosition)
  #r.MovePipetteToChipAspiratePosition(pipette, loc)
  #r.MovePipetteToChipCenterPosition(pipette, loc)
  r.PlaceChipLid(lidG, InstrumentLocation("ChipPrep-" + str(cps)))

def megaLidTest(iter, fill, load):
  if fill:
    for j in range(0, 8):
      fillStation(j, j)
  
  if load:
    r.PickupPipetteTip(Pipette.Pipette1, InstrumentLocation("TipBox-0-A01"))
    r.PickupPipetteTip(Pipette.Pipette2, InstrumentLocation("TipBox-0-A02"))
  
  for j in range(0, iter):
    print "*************************** Test iteration " + str(j)
    for i in range(0, 1):
      print "^^^^^^^^^^^^^^^^^^^^^^^^^^ Test iteration " + str(j) + ", station " + str(i)
      testStation(i, Gripper.Gripper1, Gripper.Gripper2, Pipette.Pipette1)
    
    for i in range(0, 1):
      print "%%%%%%%%%%%%%%%%%%%%%%%%%% Test iteration " + str(j) + ", station " + str(i)
      testStation(i, Gripper.Gripper2, Gripper.Gripper1, Pipette.Pipette2)

#######################
# r.Scan test

def scanTest(iter):
  r.NoScanInventory = True
  for i in range(0, iter):
    print "Iteration " + str(i)
    r.Scan()

#########################3
# Well depth calibration.

DistanceThreshold = 0.003
CalCount = 0

def calibrateWell(pipette, well):
  global CalCount
  CalCount = CalCount + 1
  print "***************************** CalCount: " + str(CalCount)
  wm = WellZMap.Instance
  loc = InstrumentLocation(well)
  nominal = wm.ZOffset(well, WellZPosition.WellBottomNominalPosition)
  try:
    r.CalibrateTipLoading(pipette)
  except:
    pass
  
  r.MovePipetteToWell(pipette, loc, 0.0)
  r.ZSpeed = ZRobotSpeed.LowSeptaSpeed
  r.CalibrateWellDepth(pipette, loc, nominal)
  r.MovePipetteToWellZPosition(pipette, loc, 0.0)
  r.ZSpeed = ZRobotSpeed.High
  rc.RaiseZ()
  # Check it, expect < 1mm offset from nominal
  mvPos = o.GetPosition(r.PipetteName(pipette) + "-" + well, False)
  calPos = o.GetPosition(r.PipetteName(pipette) + "-" + well, True)
  if abs(mvPos[2] - calPos[2]) > DistanceThreshold:
    raise "Distance calibrated to nominal too large: " + str(mvPos[2] - calPos[2])
  
  if mvPos[2] - calPos[2] == 0:
    raise "Got zero distance from nominal, fishy"

def calCorners(pipette):
  calibrateWell(pipette, "ReagentPlate0-A01")
  calibrateWell(pipette, "ReagentPlate0-A12")
  calibrateWell(pipette, "ReagentPlate0-H01")
  calibrateWell(pipette, "ReagentPlate0-H12")
  calibrateWell(pipette, "ReagentPlate1-A01")
  calibrateWell(pipette, "ReagentPlate1-A12")
  calibrateWell(pipette, "ReagentPlate1-H01")
  calibrateWell(pipette, "ReagentPlate1-H12")
  calibrateWell(pipette, "SamplePlate-A01")
  calibrateWell(pipette, "SamplePlate-A12")
  calibrateWell(pipette, "SamplePlate-H01")
  calibrateWell(pipette, "SamplePlate-H12")
  calibrateWell(pipette, "MixingPlate-A01")
  calibrateWell(pipette, "MixingPlate-A24")
  calibrateWell(pipette, "MixingPlate-P01")
  calibrateWell(pipette, "MixingPlate-P24")
  calibrateWell(pipette, "ReagentTube0-0")
  calibrateWell(pipette, "ReagentTube0-1")
  calibrateWell(pipette, "ReagentTube1-0")
  calibrateWell(pipette, "ReagentTube1-1")
  calibrateWell(pipette, "SampleTube-0")
  calibrateWell(pipette, "SampleTube-1")
  calibrateWell(pipette, "SampleTube-2")
  calibrateWell(pipette, "SampleTube-3")

def calPlate96(pipette, plate):
  for i in range(0, 12):
    for j in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'):
      calibrateWell(pipette, plate + "-" + j + zPad(i+1))

def calPlate384(pipette, plate):
  for i in range(0, 24):
    for j in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P'):
      calibrateWell(pipette, plate + "-" + j + zPad(i+1))

def calPlates(pipette):
  calPlate96(pipette, "ReagentPlate0")
  calPlate96(pipette, "ReagentPlate1")
  calPlate96(pipette, "SamplePlate")
  calPlate384(pipette, "MixingPlate")

def calAll():
  calPlates(Pipette.Pipette1)
  calPlates(Pipette.Pipette2)

def testWell(pipette, well):
  wm = WellZMap.Instance
  loc = InstrumentLocation(well)
  bottom = wm.ZOffset(well, WellZPosition.WellBottomPosition)
  r.CalibrateTipLoading(pipette)
  r.MovePipetteToWell(pipette, loc, bottom)

############################################3
# Stage MV testing

def chipToStage(gripper):
  r.CalibrateGripperToStage(gripper)
  r.PickupChip(gripper, InstrumentLocation("TestJigChip-0"))
  r.MoveChipToStage(gripper, True)

def chipFromStage(gripper):
  r.PickupChipFromStage(gripper)
  r.PlaceChip(gripper, InstrumentLocation("TestJigChip-0"))

def testCGS(iter):
  for i in range(0, iter):
    print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ test iteration: " + str(i)
    r.CalibrateGripperToStage(Gripper.Gripper1)
    r.CalibrateGripperToStage(Gripper.Gripper2)

def testChipStage(iter):
  for i in range(0, iter):
    print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ test iteration: " + str(i)
    chipToStage(Gripper.Gripper1)
    chipFromStage(Gripper.Gripper2)
    chipToStage(Gripper.Gripper2)
    chipFromStage(Gripper.Gripper1)


###############################
# Look at pipettor alignment to tip boxes

def moveToTip(pp, box, pos):
  p = o.GetPosition("Pipette" + str(pp) + "-TipBox-" + str(box) + "-" + pos)
  rc.RaiseZ()
  rc.MoveXY(p)
  rc.MoveZ(p, 2*pp)


def testPosMeanVar(nSamples, positions):
  xPos = {}
  yPos = {}
  zPos = {}
  for p in positions:
  	xPos[p] = List[Double]()
  	yPos[p] = List[Double]()
  	zPos[p] = List[Double]()
  
  for i in range(0, nSamples):
    r.Scan()
    o.InterpolateFour = True
    o.Gen96WellPlate("SampleNew4", Point2D(), "ReagentLoader-0", "ReagentLoader-0-1", "ReagentLoader-0-3", "ReagentLoader-0-2")
    o.Gen384WellPlate("MixingNew4", Point2D(-0.00225, -0.14925), "ReagentLoader-0", "ReagentLoader-0-1", "ReagentLoader-0-3", "ReagentLoader-0-2")
    o.InterpolateFour = False
    o.Gen96WellPlate("SampleNew3", Point2D(), "ReagentLoader-0", "ReagentLoader-0-1", "ReagentLoader-0-3", "ReagentLoader-0-2")
    o.Gen384WellPlate("MixingNew3", Point2D(-0.00225, -0.14925), "ReagentLoader-0", "ReagentLoader-0-1", "ReagentLoader-0-3", "ReagentLoader-0-2")
    for p in positions:
      pt = o.GetPosition(p, False)
      xPos[p].Add(pt[0])
      yPos[p].Add(pt[1])
      zPos[p].Add(pt[2])
    
      print p
      print "  x mean: " + str(Stats.Mean(xPos[p])) + ", x std: " + str(Stats.StdDev(xPos[p]))
      print "  y mean: " + str(Stats.Mean(yPos[p])) + ", y std: " + str(Stats.StdDev(yPos[p]))
      print "  z mean: " + str(Stats.Mean(zPos[p])) + ", z std: " + str(Stats.StdDev(zPos[p]))

def testNewRLPos(nSamples):
  pos = [
    "Pipette0-SamplePlate-A01", "Pipette0-SampleNew4-A01", "Pipette0-SampleNew3-A01",
    "Pipette0-SamplePlate-E07", "Pipette0-SampleNew4-E07", "Pipette0-SampleNew3-E07",
    "Pipette0-SamplePlate-H12", "Pipette0-SampleNew4-H12", "Pipette0-SampleNew3-H12",
    "Pipette0-MixingPlate-A01", "Pipette0-MixingNew4-A01", "Pipette0-MixingNew3-A01",
    "Pipette0-MixingPlate-A24", "Pipette0-MixingNew4-A24", "Pipette0-MixingNew3-A24",
    "Pipette0-MixingPlate-P01", "Pipette0-MixingNew4-P01", "Pipette0-MixingNew3-P01",
    "Pipette0-MixingPlate-P24", "Pipette0-MixingNew4-P24", "Pipette0-MixingNew3-P24"
  ]
  testPosMeanVar(nSamples, pos)

#############################################3
# Find chip in gripper

def testFindChip(holder):
  f = vt.StereoFinders['CPSChip']
  rc.RaiseZ()
  g0.SyncMoveToCPSXY()
  g0.SyncMoveToCPSZ()
  f.AcquireReferenceImage()
  rc.RaiseZ()
  r.PickupChip(Gripper.Gripper1, InstrumentLocation("TestJigChip-"+str(holder)))
  rc.RaiseZ()
  g0.SyncMoveToCPSXY()
  g0.SyncMoveToCPSZ()
  foundChip = False
  try:
    f.AcquireObject()
    foundChip = True
  except:
    pass
  if foundChip:
    print "Found chip, pos:" + str(f.ObjectPositionLeft)
  else:
    print "Did not find chip"
  
  rc.RaiseZ()
  r.PlaceChip(Gripper.Gripper1, InstrumentLocation("TestJigChip-"+str(holder)))

#fcTestLoc = "TestJigChip-"
fcTestLoc = "ChipPrep-"

def testFCPickup(cps, gripper):
  foundChip = False
  try:
    r.PickupChip(gripper, InstrumentLocation(fcTestLoc + str(cps)))
    r.PlaceChip(gripper, InstrumentLocation(fcTestLoc + str(cps)))
    foundChip = True
  except:
    pass
  
  return foundChip

def testFCPositive(cps, gripper):
  if not testFCPickup(cps, gripper):
    raise Exception("Tried to pickup chip but didn't get one")
  rc.RaiseZ()

def testFCNegative(cps, gripper):
  if testFCPickup(cps, gripper):
    raise Exception("Didn't expect to find chip, but got one anyway")
  rc.RaiseZ()

def testFC(iter):
  for i in range(0, iter):
    print "************************** Test iteration: " + str(i)
    testFCPositive(0, Gripper.Gripper1)
    testFCNegative(1, Gripper.Gripper1)
    testFCPositive(0, Gripper.Gripper2)
    testFCNegative(1, Gripper.Gripper2)

#########################################
# New stage fiducial test.

def MakeStageFinder():
  sr = vt.RealCamera(CameraNames.StageRight)
  f = StageFinder();
  f.Cam = sr
  return f

from PacBio.Common.Utils import SimplePlot

def TestStageFinder(f, iter):
  x = List[Double]()
  y = List[Double]()
  z = List[Double]()
  a = List[Double]()
  b = List[Double]()
  c = List[Double]()
  row = List[Double]()
  col = List[Double]()
  for i in range(0, iter):
    f.AcquireObject()
    pose = f.FiducialFinder.CameraPose
    x.Add(pose[0])
    y.Add(pose[1])
    z.Add(pose[2])
    a.Add(pose[3])
    b.Add(pose[4])
    c.Add(pose[5])
    row.Add(f.FiducialFinder.ResultRow[1])
    col.Add(f.FiducialFinder.ResultColumn[1])
  
  print "  x mean: " + str(Stats.Mean(x)) + ", x std: " + str(Stats.StdDev(x))
  print "  y mean: " + str(Stats.Mean(y)) + ", y std: " + str(Stats.StdDev(y))
  print "  z mean: " + str(Stats.Mean(z)) + ", z std: " + str(Stats.StdDev(z))
  print "  a mean: " + str(Stats.Mean(a)) + ", a std: " + str(Stats.StdDev(a))
  print "  b mean: " + str(Stats.Mean(b)) + ", b std: " + str(Stats.StdDev(b))
  print "  c mean: " + str(Stats.Mean(c)) + ", c std: " + str(Stats.StdDev(c))
  print "  row mean: " + str(Stats.Mean(row)) + ", row std: " + str(Stats.StdDev(row))
  print "  col mean: " + str(Stats.Mean(col)) + ", col std: " + str(Stats.StdDev(col))
  
  xm = Stats.StdDev(x)
  xm = xm * xm
  ym = Stats.StdDev(y)
  ym = ym * ym
  zm = Stats.StdDev(z)
  zm = zm * zm
  rms = Math.Sqrt(xm + ym + zm)
  print "  xyz std: " + str(rms)
  
  spr = SimplePlot()
  spr.Style = "points"
  spr.PlotTitle = "Row"
  hr = Histogram(row, 20)
  spr.AddPlotData(hr.BinCenter, hr.BinCounts)
  spr.Plot()
  
  spc = SimplePlot()
  spc.Style = "points"
  spc.PlotTitle = "Column"
  hc = Histogram(col, 20)
  spc.AddPlotData(hc.BinCenter, hc.BinCounts)
  spc.Plot()

####################3
# Fiducial repeatability test

def repeatFid(f, iter):
  x = List[Double]()
  y = List[Double]()
  z = List[Double]()
  a = List[Double]()
  b = List[Double]()
  c = List[Double]()
  row = List[Double]()
  col = List[Double]()
  rc.RaiseZ()
  rc.MoveXY(f.ImagingPos)
  for i in range(0, iter):
    f.AcquireFiducial(f.Snap())
    pose = f.FiducialPose
    x.Add(pose[0])
    y.Add(pose[1])
    z.Add(pose[2])
    a.Add(pose[3])
    b.Add(pose[4])
    c.Add(pose[5])
    row.Add(f.CircleFinder.ResultRow[0])
    col.Add(f.CircleFinder.ResultColumn[0])
  
  print "  x mean: " + str(Stats.Mean(x)) + ", x std: " + str(Stats.StdDev(x))
  print "  y mean: " + str(Stats.Mean(y)) + ", y std: " + str(Stats.StdDev(y))
  print "  z mean: " + str(Stats.Mean(z)) + ", z std: " + str(Stats.StdDev(z))
  print "  a mean: " + str(Stats.Mean(a)) + ", a std: " + str(Stats.StdDev(a))
  print "  b mean: " + str(Stats.Mean(b)) + ", b std: " + str(Stats.StdDev(b))
  print "  c mean: " + str(Stats.Mean(c)) + ", c std: " + str(Stats.StdDev(c))
  print "  row mean: " + str(Stats.Mean(row)) + ", row std: " + str(Stats.StdDev(row))
  print "  col mean: " + str(Stats.Mean(col)) + ", col std: " + str(Stats.StdDev(col))
  
  xm = Stats.StdDev(x)
  xm = xm * xm
  ym = Stats.StdDev(y)
  ym = ym * ym
  zm = Stats.StdDev(z)
  zm = zm * zm
  rms = Math.Sqrt(xm + ym + zm)
  print "  xyz std: " + str(rms)
  
  spr = SimplePlot()
  spr.Style = "points"
  spr.PlotTitle = "Row"
  hr = Histogram(row, 20)
  spr.AddPlotData(hr.BinCenter, hr.BinCounts)
  spr.Plot()
  
  spc = SimplePlot()
  spc.Style = "points"
  spc.PlotTitle = "Column"
  hc = Histogram(col, 20)
  spc.AddPlotData(hc.BinCenter, hc.BinCounts)
  spc.Plot()
