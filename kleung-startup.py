import System
import time
import math
from instrumentGlobals import *
from homerstartup import *

def log_line(f, sline):
    print sline
    if f is not None:
        f.write(sline + '\n')
        f.flush() # For tail -f

def levelRep(whichCam = CameraEnum.Yellow, initPos = None, initPosEpZ = 40e-6, initNegEpZ = 40e-6, stepsPerStack = 40, maxIters = 1,selWin=False,selWinMethod=1,VCX=40,VCY=40):
    #ill = instrument.Children["illuminationLeveler"]
    #stageLeveler=ill.stageLeveler
    if (stageLeveler.Params is None): stageLeveler.Params = LevelerParams()
    stageLeveler.PeakMethod=PeakFocusPointResult.PeakMethod.GaussianOffset1D
    stageLeveler.Params.LevelingCamera = whichCam       # Blue, Green, Yellow, Red
    if not initPos:	
        initPos = XYZabc(stage.Axis.CurrentPosition)    # the "center" position of the stack
    stageLeveler.Params.InitialPosition = initPos
    stageLeveler.Params.InitialPosEpsilonZ = initPosEpZ # how far above the center of focus to stack
    stageLeveler.Params.InitialNegEpsilonZ = initNegEpZ # how far below the center of focus to stack
    stageLeveler.Params.StepsPerStack = stepsPerStack   # how many steps to use, per stack
    stageLeveler.Params.MaxIterations = maxIters        # how many iterations to use
    stageLeveler.Params.VerticalColumnsX=VCX
    stageLeveler.Params.VerticalColumnsY=VCY
    if selWin==False:
      print "MESSAGE:using Full FRAME"+" ; IterNum:"+str(stageLeveler.Params.MaxIterations)+";Range="+str(stageLeveler.Params.InitialNegEpsilonZ)
      stageLeveler.Params.FocalConstraint = FocalConstraintEnum.FullImage
    else:
      #stageLeveler.MakeCameraSelection()
      print "MESSAGE:using Selected ROIs"+"  IterNum:"+str(stageLeveler.Params.MaxIterations)+";Range="+str(stageLeveler.Params.InitialNegEpsilonZ)
      if selWinMethod==1:
        stageLeveler.Params.FocalConstraint = FocalConstraintEnum.CameraSelectionStateWhole
      else:
        stageLeveler.Params.FocalConstraint = FocalConstraintEnum.CameraSelectionStateSubdivided
    print stageLeveler.Params.FocalConstraint
    stageLeveler.Level()
    stageLeveler.WaitForNotState(LevelerState.Idle);
    stageLeveler.WaitForState(LevelerState.Idle);
    print 'initPos =', initPos
    finalPos = XYZabc(stage.Axis.CurrentPosition) # record the final position of the chip
    print 'finalPos =', finalPos
    levelError = (finalPos-initPos)*1.0e6           # calculate the error before/after chip leveling, everything in um/urad
    print "the level error in z is "+str(levelError[2])+" um"    
    print "the level error in alpha is "+str(levelError[3])+" urad"
    print "the level error in beta is "+str(levelError[4])+" urad"
    print "..."
    return levelError

def levelChip2(camnum=4, camExposure=0.011, tiBrightness=0.14,\
initPos=None,initPosEpZ=60e-6, initNegEpZ=60e-6, stepsPerStack=30,\
stageOffset=[0,0]):
  zipit()
  print "Mode no.10:running 3 repeated lateral alignment and 1 iterations of ZMW only range"
  print "moving TI in..."
  ti.Enabled=True
  ti.VectorAxis.WaitForMove()
  tic=ti.Target.Channels[camnum-1]
  if initPos==None:
    initPos = XYZabc(stage.Axis.CurrentPosition)
  print "running routine -2, 2 iterations of full FOV"
  cam=selCamNum(camnum)
  #cam.Exposure=camExposure[0]
  #time.sleep(2)
  tic=ti.Target.Channels[camnum-1]
  #tic.Brightness=tiBrightness[0]
  #le1 = levelRep(camSel(camnum), initPos, initPosEpZ, initNegEpZ, stepsPerStack, 2,False)
  print "Chip X/Y coarse alignment"
  for cc in range(0,3): cas.BSBRChipRegistration()
  print "focus to ZMW only (1 iterations)+-"+str(initPosEpZ*1e6)+"um, AutoAxis Mode"
  cam.Exposure=camExposure
  time.sleep(2)
  tic.Brightness=tiBrightness
  le2 = levelRep(camSel(camnum), None, initPosEpZ, initNegEpZ, stepsPerStack, 1, True)
  levelError = getError(initPos)
  print "*********Start position: "+ str(initPos * 1E6)
  print "*********End position: "+ str(XYZabc(stage.Axis.CurrentPosition) * 1E6)
  #print "*********Delta position: " + str(levelError)
  return levelError

def selCamNum  (camnum):
  if camnum==1:
    whichCam = cam1
  if camnum==2:
    whichCam = cam2
  if camnum==3:
    whichCam = cam3
  if camnum==4:
    whichCam = cam4
  return whichCam

def camSel(camnum):
  if camnum==1:
    whichCam = CameraEnum.Blue
  if camnum==2:
    whichCam = CameraEnum.Green
  if camnum==3:
    whichCam = CameraEnum.Yellow
  if camnum==4:
    whichCam = CameraEnum.Red
  return whichCam

def getError(initPos):
  print 'initPos =', initPos
  finalPos = XYZabc(stage.Axis.CurrentPosition) # record the final position of the chip
  print 'finalPos =', finalPos
  levelError = (finalPos-initPos)*1.0e6           # calculate the error before/after chip leveling, everything in um/urad
  print "the level error in z is "+str(levelError[2])+" um"    
  print "the level error in alpha is "+str(levelError[3])+" urad"
  print "the level error in beta is "+str(levelError[4])+" urad"
  print "..."
  return levelError