from instrumentGlobals import *

def moveChipFromSwat2Stage( g=Gripper.Gripper1, swatChipLoc=0 ):
   try:
      chipCheck=r.RobotToStage.NoCheckForChip
      curAxisType=stage.CurrentAxisType
      stage.CurrentAxisType=StageAxisType.Coarse
      stage.Axis.TargetPosition=(0,0,0,0,0,0)
      MovementException.CheckWaitForMove(stage.Axis)
      r.RobotToStage.NoCheckForChip=True
      r.PickupChipFromStage(g)
      r.DisposeChip(g)
      r.CalibrateGripperToStage(g)
      r.PickupChip(g, InstrumentLocation("TestJigChip-" + str(swatChipLoc) ) )
      r.MoveChipToStage(g, True)
   except:
      raise
   finally:
      stage.CurrentAxisType=curAxisType
      r.RobotToStage.NoCheckForChip=chipCheck

moveChipFromSwat2Stage()
