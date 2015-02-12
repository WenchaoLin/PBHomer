from robotics import *
from testWorkflowUtil import *
from PacBio.Instrument.Protocols import WellZMap

pipetteIdealCalib(pp0, "Aqueous", 1250, 125)
pipetteIdealCalib(pp1, "Aqueous", 1250, 125)

r.ProboscisInsertionDepth=0.0066
WellZMap.Instance.SetZOffset("*a96DeepWellPlate*", WellZPosition.WellBottomPosition, 0.025)
r.ChipZOffsets[ChipZPosition.ChipBottomPosition]=0.004
r.ChipJam = False
rc.TouchChipZOffset = .006

pp0.TipId='Aqueous'
pp1.TipId='Aqueous'

f=vt.StereoFinders["StageGripper"]
ft=vt.StereoFinders["StageTip"]

global tipNum

sherriChipLocations = ((-0.211569, 0.012885,-0.0379),
                 (-0.196324, 0.012785, -0.038),
                 (-0.181397, 0.012787, -0.038),
                 (-0.166677, 0.012818, -0.0385),
                 (-0.15138, 0.012759, -0.0385),
                 (-0.135878, 0.012754, -0.0385),
                 (-0.121515, 0.012473, -0.0385),
                 (-0.106167, 0.012053, -0.0385))

# Chip locations for Amy
amyChipLocations = []
for location in sherriChipLocations:
  amyChipLocations.append(( location[0] + .008533, location[1] + .040724, location[2] - 0.001134 ))

chipLocations = amyChipLocations

def robotSetup(strip, chip):
  '''Drops initial chip to stage; Pass 0 based strip, chip location as args'''
  rc.SetZSpeed(ZRobotSpeed.Medium)
  rc.RaiseZ()
  f.Shutter=2500
  r.CalibrateGripperToStage(Gripper.Gripper1)
  #r.PickupChip(Gripper.Gripper1, InstrumentLocation("TestJigChip-1"))
  r.BreakOutChip(Gripper.Gripper1, InstrumentLocation("ChipStrip-" + str(strip) + "-" + str(chip) ))
  r.MoveChipToStage(Gripper.Gripper1, true)

def runRobotDemo(strip, chip, pause=False, manual=True):
  '''Robot Demo; Pass 0 based strip, chip location, pause at each step, manual 3D position '''

  global tipNum
  try:
    tipNum
  except NameError:
    tipNum=1
  #chip from test jig to cps
  rc.SetZSpeed(ZRobotSpeed.Medium)
  rc.RaiseZ()
  if (manual):
    xy.TargetPosition = ( chipLocations[chip][0] , chipLocations[chip][1] )  
    xy.WaitForMove()
    gp0.SetPosition(GripperState.Piercing)
    rc.MoveZ(-0.045, 1)
    gp0.SetPosition(GripperState.Engaging)
    rc.SetZSpeed(ZRobotSpeed.Low)
    rc.MoveZ( chipLocations[chip][2], 1)
    gp0.SetPosition(GripperState.Gripping)
    posBreakOut = chipLocations[chip][2] + 0.0013
    rc.SetZSpeed( ZRobotSpeed.BreakOut )

    #Turn Jam Detect off
    z.Actuator.JamCount=(0, 0, 0, 0)
    z.Actuator.JamBuffer=(0, 0, 0, 0)
    
    rc.MoveZ( posBreakOut, 1)

    #Turn Jam Detect On
    rc.SetZSpeed( ZRobotSpeed.Low )
    rc.MoveZ( chipLocations[chip][2] - .005, 1)
    rc.SetZSpeed( ZRobotSpeed.Medium )
    rc.RaiseZ()
  else:
    r.BreakOutChip(Gripper.Gripper1, InstrumentLocation("ChipStrip-" + str(strip) + "-" + str(chip) ))
  if(pause):
    raw_input("Press Enter to Continue")
  r.PickupChipLid(Gripper.Gripper2, InstrumentLocation("ChipPrep-2"))
  r.PlaceChip(Gripper.Gripper1, InstrumentLocation("ChipPrep-2"))
  r.PlaceChipLid(Gripper.Gripper2, InstrumentLocation("ChipPrep-2"))

  if(pause):
    raw_input("Press Enter to Continue")
  #pipette from from reagentplate to cps
  rc.SetZSpeed(ZRobotSpeed.High)
  well = tipTracker(tipNum)
  r.PickupPipetteTip(Pipette.Pipette1, InstrumentLocation("TipBox-0-" + well))
  tipNum=tipNum+1
  well = tipTracker(tipNum)
  r.PickupPipetteTip(Pipette.Pipette2, InstrumentLocation("TipBox-0-" + well))
  tipNum=tipNum+1
  rc.SetZSpeed(ZRobotSpeed.Medium)
  if(pause):
    raw_input("Press Enter to Continue")

  #Aspirate Wash
  r.MovePipetteToWell(Pipette.Pipette1, InstrumentLocation("ReagentPlate1-A02"), WellZMap.Instance.ZOffset(InstrumentLocation("a96DeepWellPlate"), WellZPosition.WellBottomPosition))
  pp0.Aspirate(Units.UL(20))
  rc.SetZSpeed(ZRobotSpeed.LowVibration)
  rc.RaiseZ()
  pp0.Aspirate(Units.UL(5))
  rc.SetZSpeed(ZRobotSpeed.Medium)

  #Aspirate Dispense
  if(pause):
    raw_input("Press Enter to Continue")
  r.MovePipetteToWell(Pipette.Pipette2, InstrumentLocation("ReagentPlate1-A01"), WellZMap.Instance.ZOffset(InstrumentLocation("a96DeepWellPlate"), WellZPosition.WellBottomPosition))
  pp1.Aspirate(Units.UL(20))
  rc.SetZSpeed(ZRobotSpeed.LowVibration)
  rc.RaiseZ()
  pp1.Aspirate(Units.UL(5))
  rc.SetZSpeed(ZRobotSpeed.Medium)

  if(pause):
    raw_input("Press Enter to Continue")
  r.PickupChipLid(Gripper.Gripper2, InstrumentLocation("ChipPrep-2"))  
  r.MovePipetteToWellXYPosition(Pipette.Pipette1, InstrumentLocation("ChipPrep-2"))
  r.MovePipetteToChipZPosition(Pipette.Pipette1, InstrumentLocation("ChipPrep-2"), ChipZPosition.ChipBottomPosition)
  r.MovePipetteToChipAspiratePosition(Pipette.Pipette1, InstrumentLocation("ChipPrep-2"))
  pp0.Dispense(Units.UL(25))
  pp0.Aspirate(Units.UL(30))

  if(pause):
    raw_input("Press Enter to Continue")
  r.MovePipetteToWellXYPosition(Pipette.Pipette2, InstrumentLocation("ChipPrep-2"))
  r.MovePipetteToChipZPosition(Pipette.Pipette2, InstrumentLocation("ChipPrep-2"), ChipZPosition.ChipBottomPosition)
  r.MovePipetteToChipAspiratePosition(Pipette.Pipette2, InstrumentLocation("ChipPrep-2"))
  pp1.Dispense(Units.UL(25))

  if(pause):
    raw_input("Press Enter to Continue")
  r.PlaceChipLid(Gripper.Gripper2, InstrumentLocation("ChipPrep-2"))
  rc.SetZSpeed(ZRobotSpeed.High)
  r.DisposePipetteTip(Pipette.Both)

  if(pause):
    raw_input("Press Enter to Continue")
  #remove chip from stage and place chip on stage
  rc.SetZSpeed(ZRobotSpeed.Medium)
  f.Shutter=2500
  try:
    r.CalibrateGripperToStage(Gripper.Gripper1)
  except Exception, msg:
    r.CalibrateGripperToStage(Gripper.Gripper1)

  if(pause):
    raw_input("Press Enter to Continue")
  r.PickupChipLid(Gripper.Gripper2, InstrumentLocation("ChipPrep-2"))
  r.PickupChip(Gripper.Gripper1, InstrumentLocation("ChipPrep-2"))
  r.PlaceChipLid(Gripper.Gripper2, InstrumentLocation("ChipPrep-2"))
  f.Shutter=1700

  if(pause):
    raw_input("Press Enter to Continue")
  try:
    r.PickupChipFromStage(Gripper.Gripper2)
  except Exception, msg:
    r.PickupChipFromStage(Gripper.Gripper2)
  rc.SetZSpeed(ZRobotSpeed.Medium)
  r.MoveChipToStage(Gripper.Gripper1, true)

  if(pause):
    raw_input("Press Enter to Continue")
  r.DisposeChip(Gripper.Gripper2)

  #hotstart
  rc.SetZSpeed(ZRobotSpeed.High)
  well = tipTracker(tipNum)

  if(pause):
    raw_input("Press Enter to Continue")
  r.PickupPipetteTip(Pipette.Pipette2, InstrumentLocation("TipBox-0-" + well))
  tipNum=tipNum+1
  r.MovePipetteToWell(Pipette.Pipette2, InstrumentLocation("ReagentPlate1-A03"), WellZMap.Instance.ZOffset(InstrumentLocation("a96DeepWellPlate"), WellZPosition.WellBottomPosition))
  rc.SetZSpeed(ZRobotSpeed.LowVibration)
  pp1.Aspirate(Units.UL(20))
  rc.RaiseZ()
  pp1.Aspirate(Units.UL(5))
  ft.Shutter=2500
  try:
    r.MovePipetteToStage(Pipette.Pipette2, ChipZPosition.ChipTopPosition)
  except Exception, msg:
    r.MovePipetteToStage(Pipette.Pipette2, ChipZPosition.ChipTopPosition)
  pp1.Dispense(Units.UL(25))
  rc.SetZSpeed(ZRobotSpeed.High)
  r.RemovePipetteFromStage(Pipette.Pipette2)

  if(pause):
    raw_input("Press Enter to Continue")
  r.DisposePipetteTip(Pipette.Pipette2)
  print "TipNum: " + str(tipNum)

def washJig( pause=False ):
  global tipNum
  try:
    tipNum
  except NameError:
    tipNum=1

  rc.SetZSpeed(ZRobotSpeed.High)
  well = tipTracker(tipNum)
  r.PickupPipetteTip(Pipette.Pipette1, InstrumentLocation("TipBox-0-" + well))
  tipNum=tipNum+1
  well = tipTracker(tipNum)
  r.PickupPipetteTip(Pipette.Pipette2, InstrumentLocation("TipBox-0-" + well))
  tipNum=tipNum+1
  rc.SetZSpeed(ZRobotSpeed.Medium)
  r.MovePipetteToWell(Pipette.Pipette1, InstrumentLocation("ReagentPlate1-A02"), WellZMap.Instance.ZOffset(InstrumentLocation("a96DeepWellPlate"), WellZPosition.WellBottomPosition))

  #Aspirate Wash
  pp0.Aspirate(Units.UL(20))
  rc.SetZSpeed(ZRobotSpeed.LowVibration)
  rc.RaiseZ()
  pp0.Aspirate(Units.UL(5))
  rc.SetZSpeed(ZRobotSpeed.Medium)
  r.MovePipetteToWell(Pipette.Pipette2, InstrumentLocation("ReagentPlate1-A01"), WellZMap.Instance.ZOffset(InstrumentLocation("a96DeepWellPlate"), WellZPosition.WellBottomPosition))

  #Aspirate Dispense
  pp1.Aspirate(Units.UL(20))
  rc.SetZSpeed(ZRobotSpeed.LowVibration)
  rc.RaiseZ() 
  pp1.Aspirate(Units.UL(5))
  rc.SetZSpeed(ZRobotSpeed.Medium)
  r.ChipZOffsets[ChipZPosition.ChipBottomPosition]=0.005

  if(pause):
    raw_input("Press Enter to Continue")
  r.MovePipetteToWellXYPosition(Pipette.Pipette1, InstrumentLocation("TestJigChip-0"))
  r.MovePipetteToChipZPosition(Pipette.Pipette1, InstrumentLocation("TestJigChip-0"), ChipZPosition.ChipBottomPosition)
  r.MovePipetteToChipAspiratePosition(Pipette.Pipette1, InstrumentLocation("TestJigChip-0"))
  pp0.Dispense(Units.UL(25))
  pp0.Aspirate(Units.UL(30))

  if(pause):
    raw_input("Press Enter to Continue")
  r.ChipZOffsets[ChipZPosition.ChipBottomPosition]=0.005
  r.MovePipetteToWellXYPosition(Pipette.Pipette2, InstrumentLocation("TestJigChip-0"))
  r.MovePipetteToChipZPosition(Pipette.Pipette2, InstrumentLocation("TestJigChip-0"), ChipZPosition.ChipBottomPosition)
  r.MovePipetteToChipAspiratePosition(Pipette.Pipette2, InstrumentLocation("TestJigChip-0"))
  pp1.Dispense(Units.UL(25))
  
  if(pause):
    raw_input("Press Enter to Continue")
  rc.SetZSpeed(ZRobotSpeed.High)
  r.DisposePipetteTip(Pipette.Both)
  print "TipNum: " + str(tipNum)


