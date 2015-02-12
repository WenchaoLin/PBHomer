import time
from robotics import *
from ztest import *

def localTime():
   t=time.localtime()[3:6]
   t="%i:%i:%i" % t
   return t

#Ideal location


# "Dithering" constants
dx1 = 0.0005
dy1 = 0.0005
dx2 = 0.0005
dy2 = 0.0005
dz = 0.001
zt = 0.005

robot = "Amy"

# Chip locations for Sherri
sherriChipLocations = ((-0.211569, 0.012885,-0.0379),
                 (-0.196324, 0.012785, -0.038), 
                 (-0.181397, 0.012787, -0.038),
                 (-0.166677, 0.012818, -0.0379),
                 (-0.15138, 0.012759, -0.038),
                 (-0.135878, 0.012754, -0.0383),
                 (-0.121515, 0.012473, -0.0383),
                 (-0.106167, 0.012053, -0.0382))

# Chip locations for Ralph
ralphChipLocations = []
for location in sherriChipLocations:
   ralphChipLocations.append((location[0] + 0.106972,location[1] + 0.004576, location[2] + 0.0012))

# Chip locations for Amy
amyChipLocations = []
for location in sherriChipLocations:
   amyChipLocations.append(( location[0] + .008533, location[1] + .040724, location[2] - 0.001134 ))

if robot == "Ralph":
   chipLocations = ralphChipLocations
elif robot == "Amy":
   chipLocations = amyChipLocations
elif robot == "Sherri":
   chipLocations = sherriChipLocations
else:
   chipLocations = []

def breakAllChips(gripperNum, stripOffset, chipOffset, chipsToAttempt, filename="chipBreak.txt", raiseEngaging=False, offsetXY=False, dither=True):
   """ 
   pass strip and chip location to begin chip breakout
   Breaks out each strip from right to left from top to bottom.

   gripperNum: L=1, R=0
   stripOffset: (0-11) which strip do you want to begin at (zero based)?
   chipOffset: (0-7)
   chipsToAttempt: (1-96)
   filename: Datafile stored at $dir
   raiseEngaging: False (default) or True(RaiseZ in engaging after break)
   offsetXY: If true, add X and Y offset to manual position
   """
   
   success = 0
   contSuccess = 0
   maxContSuccess = 0
   fail = 0
   chipCount = 0

   if (gripperNum == 0 ):
      myg = Gripper.Gripper1
      gIndex = 1
      mygripper = gp0
   elif (gripperNum == 1):
      myg = Gripper.Gripper2
      gIndex = 3
      mygripper = gp1

   dir = "/tmp/chipBreak/"
   #dir = "/mnt/T/SQA/Users/Simon/chipStrip/T4/"
   #dir = "c:\\temp\\"
   file = dir + filename
   fh = open(file, 'w+')
   fh.write("ChipID\tTouchRequestedZ\tTouchActualZ\tBreakOutRequestedZ\tBreakOutActualZ\n")

   #Set max distance for touch and break
   rc.TouchChipZOffset = .004
   rc.BreakChipZOffset = .006
   rc.Gripper1TouchForceDelta = .3

   #for i in range(12):
   for i in (1,2,5,6,9,10): #for modified T4 tray
      if ( i < stripOffset ):
         continue
      if (chipCount >= chipsToAttempt):
      #break out of for loop if we reach desired number of chips
         continue
      for j in range (8):
         if (( i == stripOffset ) and ( j < chipOffset )):
            continue
         if (chipCount >= chipsToAttempt):
         #break out of inner for loop if we reach desired number of chips
            continue
         chipCount = chipCount + 1
         print "Attempting Chip Break(0): Strip" + str(i) + " Chip" + str(j)
         posAboveFoil = -0.05
         posAboveChip = ""
         posEnterCell = ""
         posTouchChip = ""
         posPostWiggle = ""
         posBreakOut = ""
         posBreakOutActual = ""
         distBreakChip = .005
         if (offsetXY):
            distXOffset = 0.0005
            distYOffset = -0.0005
         else:
            distXOffset = 0
            distYOffset = 0
         fh.write("\n")
         mytime = ""


         #Move above cell 
         try:
            rc.RaiseZ() 

            #Manual positioning
            xy.TargetPosition = ( chipLocations[j][0] + distXOffset, chipLocations[j][1] + distYOffset )
            xy.WaitForMove()
            #r.MoveAboveChip(myg, InstrumentLocation("ChipStrip-" + str(i) + "-" + str(j)))
            posTarget = z.CurrentPosition
            posTarget[gIndex] = posAboveFoil
            z.TargetPosition = posTarget
            z.WaitForMove()
            
            mytime = localTime()
            posAboveChip = z.CurrentPosition[gIndex]
            time.sleep(1)
         except Exception, msg:
            print "Move Above Chip Error: " + str(msg)
            posAboveChip = "Fail"
            rc.RaiseZ()
            continue


         """
         #Adjust for XY offset
         myX = xy.CurrentPosition[0]
         myY = xy.CurrentPosition[1]
         posX = xy.CurrentPosition[0] - .0002
         posY = xy.CurrentPosition[1] - .0008
         #posY = xy.CurrentPosition[1]
         xy.Controller.SetSlowMotionProfile()
         xy.TargetPosition = (posX,posY)
         xy.WaitForMove()
         time.sleep(5)
         xy.Controller.SetMediumMotionProfile()
         """






         
         #Temp hack to pierce and grip chip.
         mygripper.SetPosition(GripperState.Piercing)
         time.sleep(2)
         
         #insert into cell
         if robot == "Ralph":
            posInCell = -0.042
         elif robot == "Sherri":
            posInCell = -0.045
         
         rc.MoveZ( posInCell, gIndex)
         mygripper.SetPosition(GripperState.Engaging)
         time.sleep(2)
         z.Actuator.Tolerance = (.25, .25, .25, .25)
         z.Actuator.StepSize = (1,1,1,1)
         z.Actuator.MinVelocity = (.001, .001, .001, .001)
         z.Actuator.MaxVelocity = (.001, .001, .001, .001)
         rc.MoveZ( chipLocations[j][2], gIndex)
         fh.write( str(i) + "-" + str(j) + "\t" + str(chipLocations[j][2]) + "\t" + str(z.CurrentPosition[gIndex]) )
         




         
         """
         #Pierce FOIL
         try:
            #breakChip(g, i, j)
            r.PierceFoilForChip(myg, InstrumentLocation("ChipStrip-" + str(i) + "-" + str(j)))

         except Exception, msg:
            print "Pierce Error: " + str(msg)
            #posAboveChip = "Fail" #FIXME
            rc.RaiseZ()
            continue
         finally: 
            fh.write( mytime + "\t" + str(i) + "-" + str(j) + "\t" + str(posAboveChip) ) #FIXME, why twice?
         """


         """
         #Touch CHIP
         try:
            #plotForce("10.10.4.164", gIndex, 30, "Approaching Touch")
            posTarget = z.CurrentPosition
            posEnterCell = z.CurrentPosition[gIndex]
            posEnterCell = posEnterCell + 0.002
            posTarget[gIndex] = posEnterCell
            z.TargetPosition = posTarget
            z.WaitForMove()

            
            r.TouchChip(myg, InstrumentLocation("ChipStrip-" + str(i) + "-" + str(j)))
            posTouchChip = z.CurrentPosition[gIndex]
            time.sleep(3)
            mygripper.SetPosition(GripperState.Gripping)
            time.sleep(1)
         
         except Exception, msg:
            print "Touch Chip Error: " + str(msg)
            posTouchChip = "Fail"
            rc.RaiseZ()
            xy.TargetPosition = (0,0)
            xy.WaitForMove()
            mygripper.SetPosition(GripperState.Engaging)
            continue
         finally:
            fh.write( "\t" + str(posTouchChip) )
         """


         """
         #Set position for Z wiggle and XY wiggle
         time.sleep(1)
         posTarget = z.CurrentPosition
         posWeaken = posTouchChip + .0004
         posWeaken2 = posTouchChip + .0006
         #posBreakOut = posTouchChip + 0.0004 #now with respect to raised position
         #posTarget[gIndex] = posBreakOut
         z.Actuator.MaxVelocity = (.001, .001, .001, .001)
         z.Actuator.MinVelocity = (.001, .001, .001, .001)
         print "Weakening chip"

         #XY chip wiggle
         myX = xy.CurrentPosition[0]
         myY = xy.CurrentPosition[1]
         posXRight = myX + .001
         posXLeft = myX - .001

         #drivesOff()

         #XY wiggle
         xy.Controller.SetSlowMotionProfile()
         raw_input("Press Enter to Continue")
         #xy.TargetPosition = (posXLeft,myY)
         #xy.WaitForMove()
         raw_input("Press Enter to Continue")
         #print "Moving XY from: " + str(posXYLeft)  + " to :" + str(posXYRight)
         xy.TargetPosition = (posXRight,myY)
         xy.WaitForMove()
         raw_input("Press Enter to Continue")
         #print "Moving XY from: " + str(posXYRight) + " to :" + str(myxy)
         xy.TargetPosition = (myX,myY)
         xy.WaitForMove()

         xy.Controller.SetMediumMotionProfile()
         """

         """
         #Z wiggle
         z.Actuator.MaxVelocity = (.004, .004, .004, .004)
         z.Actuator.MinVelocity = (.004, .004, .004, .004)

         for k in range (10):
            posTarget[gIndex] = posWeaken
            z.TargetPosition = posTarget
            z.WaitForMove()
            posTarget[gIndex] = posTouchChip
            z.TargetPosition = posTarget
            z.WaitForMove()

         for k in range (10):
            posTarget[gIndex] = posWeaken2
            z.TargetPosition = posTarget
            z.WaitForMove()
            posTarget[gIndex] = posTouchChip
            z.TargetPosition = posTarget
            z.WaitForMove()

         posPostWiggle = z.CurrentPosition[gIndex]
         fh.write( "\t" + str(posPostWiggle) )

         #Raise Z slightly before break
         posPreBreak = z.CurrentPosition[gIndex]
         posPreBreak = posPreBreak - .0001 
         posTarget[gIndex] = posPreBreak
         z.TargetPosition = posTarget
         z.WaitForMove()
         posPreBreak = z.CurrentPosition[gIndex]
         fh.write( "\t" + str(posPreBreak) )
         """

         
         print "Breaking Chip"

         """
         quit = raw_input("Press Enter to break out chip, or q to quit: ")
         if (quit == 'q'):
            z.Actuator.Tolerance = (.25, .25, .25, .25)
            z.Actuator.StepSize = (1,1,1,1)
            z.Actuator.MaxVelocity = (.25, .25, .25, .25)
            z.Actuator.MinVelocity = (.05, .05, .05, .05)
            break
         #Try breaking out with full steps and high velocity
         """

         mygripper.SetPosition(GripperState.Gripping)
         time.sleep(1)

         z.Actuator.Tolerance = (.25,.25,.25,.25)
         z.Actuator.StepSize = (1,1,1,1)
         
         z.Actuator.MinVelocity = (.15, .15, .15, .15)
         z.Actuator.MaxVelocity = (.15, .15, .15, .15)
         
         #posBreakOut = posPreBreak + .0006
         posBreakOut = chipLocations[j][2] + distBreakChip
         #was + .0005

         for k in range(1):
            posTarget = z.CurrentPosition
            posTarget[gIndex] = posBreakOut
            z.TargetPosition = posTarget
            z.WaitForMove()
            posBreakOutActual = z.CurrentPosition[gIndex]
            time.sleep(.2)

            if dither == True:
               #Slowly raise Z
               z.Actuator.Tolerance = (.25, .25, .25, .25)
               z.Actuator.StepSize = (1,1,1,1)
               z.Actuator.MinVelocity = (.001, .001, .001, .001)
               z.Actuator.MaxVelocity = (.001, .001, .001, .001)
            
               #posTarget = z.CurrentPosition
               #posTarget[gIndex] -= dz
               #z.TargetPosition = posTarget
               #z.WaitForMove()
            
               # Move in X and Y to attempt to fold tab remnants
               curPos = xy.CurrentPosition
               xy.TargetPosition = (curPos[0] + dx1, curPos[1])
               time.sleep(1)
            
               xy.TargetPosition = (curPos[0] + dx1, curPos[1] + dy1)
               time.sleep(1)

               xy.TargetPosition = (curPos[0] - dx1, curPos[1] + dy1)
               time.sleep(1)

               xy.TargetPosition = (curPos[0] - dx1, curPos[1] - dy1)
               time.sleep(1)

               xy.TargetPosition = (curPos[0], curPos[1] - dy1)
               time.sleep(1)

               xy.TargetPosition = (curPos[0], curPos[1])
               time.sleep(1)
            
            #For trouble shooting whether there was a complete break before raising
            if (raiseEngaging):
               mygripper.SetPosition(GripperState.Engaging)
               time.sleep(.2)

            #Raise to prebreak location
            #posTarget[gIndex] = chipLocations[j][2]
            #z.TargetPosition = posTarget
            #z.WaitForMove()

         #raw_input("Press Enter to Raise Z")
         #print "Raise Z"

         #Slowly raise Z

         z.Actuator.Tolerance = (.25, .25, .25, .25)
         z.Actuator.StepSize = (1,1,1,1)
         z.Actuator.MinVelocity = (.001, .001, .001, .001)
         z.Actuator.MaxVelocity = (.001, .001, .001, .001)

         # "Dither chip to unstick gripper from cell wall"
         if dither == True:
            zt_traveled = 0
            while (zt_traveled < zt):
               posTarget = z.CurrentPosition
               posTarget[gIndex] -= dz
               z.TargetPosition = posTarget
               z.WaitForMove()
               
               curPos = xy.CurrentPosition
               xy.TargetPosition = (curPos[0] + dx2, curPos[1])
               time.sleep(1)
                
               xy.TargetPosition = (curPos[0] + dx2, curPos[1] + dy1)
               time.sleep(1)
                
               xy.TargetPosition = (curPos[0] + dx2, curPos[1] - dy1)
               time.sleep(1)
                
               xy.TargetPosition = (curPos[0] + dx2, curPos[1])
               time.sleep(1)
                
               xy.TargetPosition = (curPos[0], curPos[1])
               time.sleep(1)
                
               xy.TargetPosition = (curPos[0], curPos[1] + dy1)
               time.sleep(1)
                
               xy.TargetPosition = (curPos[0], curPos[1] - dy1)
               time.sleep(1)
                
               xy.TargetPosition = (curPos[0], curPos[1])
               time.sleep(1)
                
               xy.TargetPosition = (curPos[0] - dx2, curPos[1])
               time.sleep(1)
                
               xy.TargetPosition = (curPos[0] - dx2, curPos[1] + dy1)
               time.sleep(1)
                
               xy.TargetPosition = (curPos[0] - dx2, curPos[1] - dy1)
               time.sleep(1)
                
               xy.TargetPosition = (curPos[0] - dx2, curPos[1])
               time.sleep(1)
                
               xy.TargetPosition = (curPos[0], curPos[1])
               time.sleep(1)

               zt_traveled += dz

         posTarget = z.CurrentPosition
         posTarget[gIndex] = posTarget[gIndex] - .005
         z.TargetPosition = posTarget
         z.WaitForMove()

         #Fast raise Z
         z.Actuator.MaxVelocity = (.25, .25, .25, .25)
         z.Actuator.MinVelocity = (.05, .05, .05, .05)
         rc.RaiseZ()

         if (raiseEngaging):
            continue

         xy.TargetPosition = (0.133706, 0.054622)
         xy.WaitForMove()
         quit = raw_input("Press Enter to Drop Chip, q to quit: ")
         if (quit == 'q'):
            break
         mygripper.SetPosition(GripperState.Engaging)
         time.sleep(1)
         fh.write( "\t" + str(posBreakOut) + "\t" + str(posBreakOutActual) )


         """
         #START
         try:
            r.MoveAboveChip(myg, InstrumentLocation("ChipStrip-" + str(i) + "-" + str(j)))
            #plotForce("10.10.4.164", gIndex, 30, "Breaking Chip")
            r.BreakTabsForChip(myg, InstrumentLocation("ChipStrip-" + str(i) + "-" + str(j)))
            posBreakOut = z.CurrentPosition[gIndex]
            success = success + 1
            contSuccess = contSuccess + 1
            if ( contSuccess > maxContSuccess ):
               maxContSuccess = contSuccess
         except Exception, msg:
            print "BreakChip Error: " + str(msg)
            posBreakOut = "Fail"
            fail = fail + 1
            contSuccess = 0
         finally:
            time.sleep(1)
            rc.RaiseZ()
            fh.write( "\t" + str(posBreakOut) )
            # Go to waste position
            #xy.TargetPosition = (-0.798778, -0.196315)
            xy.TargetPosition = (0.126821, 0.047891)
            xy.WaitForMove()
            mygripper.SetPosition(GripperState.Engaging)
            time.sleep(1)

   print "Success: " + str(success)
   print "Max Continuous Success: " + str(maxContSuccess)
   print "Failures: " + str(fail)
         #END
         """

   fh.write("\n")
   fh.close()
