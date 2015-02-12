from PacBio.Instrument.Homer import *
from PacBio.Instrument.Vision import *
from PacBio.Common.Numeric import *
from PacBio.Instrument.Interfaces import *
from PacBio.Instrument.Interfaces.Fluidics import *
from PacBio.Instrument.Interfaces.Homer import *
from PacBio.Instrument.Interfaces.Movement import *
from PacBio.Instrument.Interfaces.Vision import *
import time
import math

CTaxis = InstrumentContext.Instrument.ChipsTipsDrawer.ChipTipAxisDrawer.Axis
RLaxis = InstrumentContext.Instrument.TemplateReagentDrawer.ReagentAxisDrawer.Axis
CTdrawer = InstrumentContext.Instrument.ChipsTipsDrawer
RLdrawer = InstrumentContext.Instrument.TemplateReagentDrawer
CTlim = CTaxis.LimitSwitches
RLlim = RLaxis.LimitSwitches
	
def print_lims(myaxis):
	myaxis.LimitSwitches.PosLimitOn = True;
	print "Negative limit blocked:", myaxis.LimitSwitches.NegLimit
	print "Positive limit blocked:", myaxis.LimitSwitches.PosLimit
	
def disable_motor(myaxis):
	myaxis.Enabled = False
	
def enable_motor(myaxis):
	myaxis.Enabled = True
	
def open_test_axis(myaxis):
	if (not myaxis.Encoder.IsValid) or (not myaxis.Encoder.HasCount):
		print "Encoder is not valid or doesn't have a count. Quitting."
		return
	print "The drawer will now open."
	temp=raw_input("Press Enter to continue")
	enc1=myaxis.Encoder.CurrentPosition
	enc1count=myaxis.Encoder.CurrentCount
	myaxis.TargetPosition = 0.40
	print "Axis moving:", myaxis.IsMoving
	print "Target position:", myaxis.TargetPosition
	#wait for opening to end
	while myaxis.IsMoving == True:
		time.sleep(0.25)
		print "Position:", myaxis.CurrentPosition
	print "Axis moving:", myaxis.IsMoving
	enc2=myaxis.Encoder.CurrentPosition
	enc2count=myaxis.Encoder.CurrentCount
	print "Position changed:", (enc2-enc1)
	print "Encoder count changed:", (enc2count-enc1count)
	#print "Position change should be around 0.4"
	#print "Encoder count change should be around 62k"
	#temp=raw_input("Do the position and encoder count change numbers make sense?")

def close_test_axis(myaxis):
	if (not myaxis.Encoder.IsValid) or (not myaxis.Encoder.HasCount):
		print "Encoder is not valid or doesn't have a count. Quitting."
		return
	if myaxis.IsMoving:
		print "The axis is moving. Waiting for it to finish."
		while myaxis.IsMoving == True:
			time.sleep(0.25)
	print "The drawer will now close."
	temp=raw_input("Press Enter to continue")
	enc1=myaxis.Encoder.CurrentPosition
	enc1count=myaxis.Encoder.CurrentCount
	myaxis.TargetPosition = 0
	print "Axis moving:", myaxis.IsMoving
	print "Target position:", myaxis.TargetPosition
	#wait for closing to end
	while myaxis.IsMoving == True:
		time.sleep(0.25)
		print "Position:", myaxis.CurrentPosition
	print "Axis moving:", myaxis.IsMoving
	enc2=myaxis.Encoder.CurrentPosition
	enc2count=myaxis.Encoder.CurrentCount
	print "Position changed:", (enc2-enc1)
	print "Encoder count changed:", (enc2count-enc1count)
	
def open_test_drawer(mydrawer, myaxis):
	temp=raw_input("Timing opening of drawer. It will close first. Press enter.")
	mydrawer.Close()
	t0=time.clock()
	p0=myaxis.CurrentPosition
	e0=myaxis.Encoder.CurrentCount
	mydrawer.Open()
	t1=time.clock()
	p1=myaxis.CurrentPosition
	e1=myaxis.Encoder.CurrentCount
	s1=1000*(p1-p0)/(t1-t0)
	print "Encoder recorded a change of", e1-e0, "counts."
	print "Opened", p1-p0, "m in", t1-t0, "seconds."
	print "The drawer opened at an average speed of", s1, "mm/s."

def close_test_drawer(mydrawer, myaxis):
	temp=raw_input("Timing closing of drawer. It will open first. Press enter.")
	mydrawer.Open()
	t0=time.clock()
	p0=myaxis.CurrentPosition
	e0=myaxis.Encoder.CurrentCount
	mydrawer.Close()
	t1=time.clock()
	p1=myaxis.CurrentPosition
	e1=myaxis.Encoder.CurrentCount
	s1=1000*(p1-p0)/(t1-t0)
	print "Encoder recorded a change of", e1-e0, "counts."
	print "Closed", p1-p0, "m in", t1-t0, "seconds."
	print "The drawer closed at an average speed of", s1, "mm/s."

def run_drawer_tests(mydrawer):
	myaxis=mydrawer.GetLoader().Axis
	print_lims(myaxis)
	disable_motor(myaxis)
	print "Beginning Manual Sensor Test. Drawer motor disabled."
	print_lims(myaxis)
	e1 = myaxis.Encoder.CurrentCount
	p1 = myaxis.Encoder.CurrentPosition
	temp = raw_input("Move the drawer so neither limit switch is blocked. Press enter.")
	mycount = 0
	myaxis.LimitSwitches.NegLimitOn = True
	neg_lim = myaxis.LimitSwitches.NegLimit
	pos_lim = myaxis.LimitSwitches.PosLimit
	while (neg_lim and pos_lim and mycount<20): #5 seconds
		time.sleep(0.25)
		myaxis.LimitSwitches.NegLimitOn=True;
		neg_lim = myaxis.LimitSwitches.NegLimit
		pos_lim = myaxis.LimitSwitches.PosLimit
		mycount = mycount+1
	e2 = myaxis.Encoder.CurrentCount
	p2 = myaxis.Encoder.CurrentPosition
	if (not neg_lim and not pos_lim):
		print "Passed."
		print "Encoder moved", e2-e1, "counts."
		print "Encoder reports a position move of", p2-p1, "meters."
	if neg_lim:
		print "Negative limit blocked."
	if pos_lim:
		print "Positive limit blocked."
	if mycount==20:
		print "Limit switch read timed out."
	mycount = 0
	temp = raw_input("Close the drawer to block the negative limit switch. Press enter.")
	myaxis.LimitSwitches.NegLimitOn=True;
	neg_lim = myaxis.LimitSwitches.NegLimit
	pos_lim = myaxis.LimitSwitches.PosLimit
	while (not neg_lim and pos_lim and mycount<20):
		time.sleep(0.25)
		myaxis.LimitSwitches.NegLimitOn=True;
		neg_lim = myaxis.LimitSwitches.NegLimit
		pos_lim = myaxis.LimitSwitches.PosLimit
		mycount = mycount+1
	e3 = myaxis.Encoder.CurrentCount
	p3 = myaxis.Encoder.CurrentPosition
	if (neg_lim and not pos_lim):
		print "Passed."
		print "Encoder moved", e3-e2, "counts."
		print "Encoder reports a position move of", p3-p2, "meters."
	if not neg_lim:
		print "Negative limit not blocked."
	if pos_lim:
		print "Positive limit blocked."
	if mycount==20:
		print "Limit switch read timed out."
	mycount = 0
	temp = raw_input("Open the drawer to block the positive limit switch. Press enter.")
	myaxis.LimitSwitches.NegLimitOn=True;
	neg_lim = myaxis.LimitSwitches.NegLimit
	pos_lim = myaxis.LimitSwitches.PosLimit
	while (neg_lim and not pos_lim and mycount<20):
		time.sleep(0.25)
		myaxis.LimitSwitches.NegLimitOn=True;	
		neg_lim = myaxis.LimitSwitches.NegLimit
		pos_lim = myaxis.LimitSwitches.PosLimit
		mycount = mycount+1
	e4 = myaxis.Encoder.CurrentCount
	p4 = myaxis.Encoder.CurrentPosition
	if not neg_lim and pos_lim:
		print "Passed."
		print "Encoder moved", e4-e3, "counts."
		print "Encoder reports a position move of", p4-p3, "meters."
	if not neg_lim:
		print "Negative limit blocked."
	if pos_lim:
		print "Positive limit not blocked."
	if mycount==20:
		print "Limit switch read timed out."
	print "End of Manual Sensor Test."
	temp = raw_input("Do you want to continue? (y/n)")
	if (temp=="y" or temp=="Y"):
		pass
	else:
		return
	print "Continuing the test."
	enable_motor(myaxis)
	print "Axis configured:", myaxis.IsConfigured
	print "Axis initialized:", myaxis.IsInitialized
	print "Axis current position:", myaxis.CurrentPosition
	myaxis.TargetPosition = 0;
	open_test_axis(myaxis)
	print_lims(myaxis)
	close_test_axis(myaxis)
	print_lims(myaxis)
	temp = raw_input("Do you want to continue? (y/n)")
	if (temp=="y" or temp=="Y"):
		pass
	else:
		return
	open_test_drawer(mydrawer, myaxis)
	print_lims(myaxis)
	close_test_drawer(mydrawer, myaxis)
	print_lims(myaxis)