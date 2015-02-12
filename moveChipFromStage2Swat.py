from instrumentGlobals import *

def moveChipFromStage2Swat( g=Gripper.Gripper1, swatChipLoc=0 ):
   try:
      curAxisType=stage.CurrentAxisType
      stage.CurrentAxisType=StageAxisType.Coarse
      stage.Axis.TargetPosition=(0,0,0,0,0,0)
      MovementException.CheckWaitForMove(stage.Axis)
      r.PickupChipFromStage(g)
      r.PlaceChip(g, InstrumentLocation("TestJigChip-" + str(swatChipLoc) ) )
   except:
      raise
   finally:
      stage.CurrentAxisType=curAxisType

moveChipFromStage2Swat()
