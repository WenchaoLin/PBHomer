from PacBio.Instrument.Homer import *
from PacBio.Instrument.Vision import *
from PacBio.Common.Numeric import *
from PacBio.Instrument.Interfaces.Homer import *
from PacBio.Instrument.Interfaces.Movement import *
from PacBio.Instrument.Interfaces.Vision import *
from PacBio.Instrument.RT import *
from System import *
import copy
import time
import clr
import string
import math
from HalconDotNet import *

instrument = InstrumentContext.Instrument
a = instrument.Robot.XYAxes
vt = instrument.Robot.VisionTools;
cam = vt.RealCamera("ZCamera")

tip0 = vt.Fiducials["TipNest-0"]
tip1 = vt.Fiducials["TipNest-1"]
tray0 = vt.Fiducials["ChipTray-0"]
tray1 = vt.Fiducials["ChipTray-1"]
tray2 = vt.Fiducials["ChipTray-2"]
tray3 = vt.Fiducials["ChipTray-3"]
pf0 = None
pf1 = None

def prepare():
  vt.Oracle.Find()

def scan():
  global pf0
  global pf1
  resultPoints = {}
  a.TargetPosition = tip0.RobotPositionToCenter((0, 0, 0))
  a.WaitForMove()
  tip0.CircleFinder.Find(tip0.Snap(), tip0)
  
  a.TargetPosition = tip0.RobotPositionToCenter((0, 0.1115, 0))
  a.WaitForMove()
  tip0.CircleFinder.Find(tip0.Snap(), tip0)
  
  a.TargetPosition = tray0.RobotPositionToCenter((0, 0.07975, 0))
  a.WaitForMove()
  tray1.CircleFinder.Find(tray1.Snap(), tray1)
  
  a.TargetPosition = tray0.RobotPositionToCenter((0.1594, 0.07975, 0))
  a.WaitForMove()
  tray3.CircleFinder.Find(tray3.Snap(), tray3)
  
  a.TargetPosition = tray0.RobotPositionToCenter((0.1594, 0.0, 0))
  a.WaitForMove()
  tray2.CircleFinder.Find(tray2.Snap(), tray2)
  
  resultPoints["p0-p1"] = (tray1.CircleFinder.ResultRow[2], tray1.CircleFinder.ResultColumn[2])
  resultPoints["p0-p2"] = (tray2.CircleFinder.ResultRow[2], tray2.CircleFinder.ResultColumn[2])
  resultPoints["p0-p3"] = (tray3.CircleFinder.ResultRow[2], tray3.CircleFinder.ResultColumn[2])
  
  pf0 = (tray1.CircleFinder.ResultRow[0], tray1.CircleFinder.ResultColumn[0])
  pf1 = (tray1.CircleFinder.ResultRow[7], tray1.CircleFinder.ResultColumn[7])
  
  a.TargetPosition = tray1.RobotPositionToCenter((0, -0.07975, 0))
  a.WaitForMove()
  tray0.CircleFinder.Find(tray1.Snap(), tray0)
  
  a.TargetPosition = tray1.RobotPositionToCenter((0.1594, -0.07975, 0))
  a.WaitForMove()
  tray2.CircleFinder.Find(tray3.Snap(), tray2)
  
  a.TargetPosition = tray1.RobotPositionToCenter((0.1594, 0.0, 0))
  a.WaitForMove()
  tray3.CircleFinder.Find(tray1.Snap(), tray3)
  
  resultPoints["p1-p0"] = (tray0.CircleFinder.ResultRow[2], tray0.CircleFinder.ResultColumn[2])
  resultPoints["p1-p2"] = (tray2.CircleFinder.ResultRow[2], tray2.CircleFinder.ResultColumn[2])
  resultPoints["p1-p3"] = (tray3.CircleFinder.ResultRow[2], tray3.CircleFinder.ResultColumn[2])
  
  a.TargetPosition = tray2.RobotPositionToCenter((0, 0.07975, 0))
  a.WaitForMove()
  tray3.CircleFinder.Find(tray3.Snap(), tray3)
  
  a.TargetPosition = tray2.RobotPositionToCenter((-0.1594, 0.07975, 0))
  a.WaitForMove()
  tray1.CircleFinder.Find(tray1.Snap(), tray1)
  
  a.TargetPosition = tray2.RobotPositionToCenter((-0.1594, 0.0, 0))
  a.WaitForMove()
  tray0.CircleFinder.Find(tray0.Snap(), tray0)
  
  resultPoints["p2-p3"] = (tray3.CircleFinder.ResultRow[2], tray3.CircleFinder.ResultColumn[2])
  resultPoints["p2-p1"] = (tray1.CircleFinder.ResultRow[2], tray1.CircleFinder.ResultColumn[2])
  resultPoints["p2-p0"] = (tray0.CircleFinder.ResultRow[2], tray0.CircleFinder.ResultColumn[2])
  
  a.TargetPosition = tray3.RobotPositionToCenter((0, -0.07975, 0))
  a.WaitForMove()
  tray2.CircleFinder.Find(tray2.Snap(), tray2)
  
  a.TargetPosition = tray3.RobotPositionToCenter((-0.1594, -0.07975, 0))
  a.WaitForMove()
  tray0.CircleFinder.Find(tray0.Snap(), tray0)
  
  a.TargetPosition = tray3.RobotPositionToCenter((-0.1594, 0.0, 0))
  a.WaitForMove()
  tray1.CircleFinder.Find(tray1.Snap(), tray1)
  
  resultPoints["p3-p2"] = (tray2.CircleFinder.ResultRow[2], tray2.CircleFinder.ResultColumn[2])
  resultPoints["p3-p0"] = (tray0.CircleFinder.ResultRow[2], tray0.CircleFinder.ResultColumn[2])
  resultPoints["p3-p1"] = (tray1.CircleFinder.ResultRow[2], tray1.CircleFinder.ResultColumn[2])
  return resultPoints

#XY coordinates in meters
p0 = (0.0, 0.0)
p1 = (0.0, 0.07975)
p2 = (0.1594, 0.0)
p3 = (0.1594, 0.07975)

def distanceP2P(p1, p2):
  dr = p1[0] - p2[0] #y
  dc = p1[1] - p2[1] #x
  dr = dr * dr
  dc = dc * dc
  d = math.sqrt(dr + dc)
  return d #pixel error

def distanceXYP2P(p1, p2):
  dy = p1[0] - p2[0]
  dx = p1[1] - p2[1]
  return dx, dy

def distanceFromNominal(p):
  return distanceP2P(p, (384, 512))

def distanceFromNominalXY(p):
  return distanceXYP2P(p, (384, 512))

def errorPerMM(p1, p2, p):
  dt = distanceP2P(p1, p2)
  de = distanceFromNominal(p)
  dt = dt * 1000 # Convert to mm
  return de / dt

#mmPerPix = 40 / distanceP2P(pf0, pf1)

maxDistErr = 0.0
minDistErr = 10000
worstDistErr = ""
maxErrPerMM = 0.0
minErrPerMM = 10000
worstErrPerMM = ""
sumErrPerMM = 0.0
countErrPerMM = 0.0

def resetStats():
  global maxDistErr
  global minDistErr
  global worstDistErr
  global maxErrPerMM
  global minErrPerMM
  global worstErrPerMM
  global sumErrPerMM
  global countErrPerMM
  maxDistErr = 0.0
  minDistErr = 10000
  maxErrPerMM = 0.0
  minErrPerMM = 10000
  sumErrPerMM = 0.0
  countErrPerMM = 0.0

def recordStats(distErr, errPerMM, label):
  global maxDistErr
  global minDistErr
  global worstDistErr
  global maxErrPerMM
  global minErrPerMM
  global worstErrPerMM
  global sumErrPerMM
  global countErrPerMM
  if maxDistErr < distErr:
    maxDistErr = distErr
    worstDistErr = label
  
  minDistErr = min(minDistErr, distErr)
  if maxErrPerMM < errPerMM:
    maxErrPerMM = errPerMM
    worstErrPerMM = label
  
  minErrPerMM = min(minErrPerMM, errPerMM)
  sumErrPerMM = sumErrPerMM + errPerMM
  countErrPerMM = countErrPerMM + 1.0

def reportStats():
  print "max distance error   = " + str(maxDistErr)
  print "min distance error   = " + str(minDistErr)
  print "worst move, dist err : " + worstDistErr
  print "max error per mm     = " + str(maxErrPerMM)
  print "min error per mm     = " + str(minErrPerMM)
  print "worst move, per mm   : " + worstErrPerMM
  print "average error per mm = " + str(sumErrPerMM / countErrPerMM)

def report1(label, pa, pb, results):
  mmPerPix = 40 / distanceP2P(pf0, pf1)
  papb = results[label]
  pixErr = distanceFromNominal(papb)
  xPixErr, yPixErr = distanceFromNominalXY(papb)
  distErr = pixErr * mmPerPix
  errPerMM = errorPerMM(pa, pb, papb)
  recordStats(distErr, errPerMM, label)
  print label
  print "  distance       = " + str(distanceP2P(pa, pb))
  print "  pix error      = " + str(pixErr)
  print "  pix error x    = " + str(xPixErr)
  print "  pix error y    = " + str(yPixErr)
  print "  distance error = " + str(distErr)
  print "  pix err per mm = " + str(errPerMM)

def report(results):
  resetStats()
  
  report1("p0-p1", p0, p1, results)
  report1("p0-p2", p0, p2, results)
  report1("p0-p3", p0, p3, results)
  
  report1("p1-p0", p1, p0, results)
  report1("p1-p2", p1, p2, results)
  report1("p1-p3", p1, p3, results)
  
  report1("p2-p0", p2, p0, results)
  report1("p2-p1", p2, p1, results)
  report1("p2-p3", p2, p3, results)
  
  report1("p3-p0", p3, p0, results)
  report1("p3-p1", p3, p1, results)
  report1("p3-p2", p3, p2, results)
  
  print ""
  print "mm/pixel = " + str(40 / distanceP2P(pf0, pf1))
  print ""
  reportStats()

def runTest():
  prepare()
  results = scan()
  report(results)

def runQuick():
  results = scan()
  report(results)


