#
# david's standard homer debug environmnet
#

import clr
import time
import random

from System import *
from System.Collections import *
from System.Collections.Generic import *

from PacBio.Instrument.RT import *
from PacBio.Instrument.Devices import *
from PacBio.Instrument.Interfaces import *

from PacBio.Common.Numeric import *
from PacBio.Common.Utils import *
from PacBio.Instrument.Devices import *
from PacBio.Instrument.Environmental import *
from PacBio.Instrument.Homer import *
from PacBio.Instrument.Interfaces import *
from PacBio.Instrument.RT import *

# for the serial bits to play with
from PacBio.Common.IO.Serial import *

# shortcut because my memory sucks

def runfaster():
	allowEarlyStarts()

from protocols import *
def RunOneChipNoPipeline():
    """Do all the stuff needed to run acqusition and analysis protocols on a single test chip WITHOUT a pipeline.exe running"""
    runfaster()
    DeleteInventoryData()
    ImportSS(exedir + pds + 'Protocols' + pds + 'oneWellSSNoTraces.csv')
    return WaitForRun(RunSamplePlate())

# Dan's Drawer Board

test_board = "10.10.4.167"
#led = RTBoard.Get(IPanelLED, test_board, "/panelled")

# Design Lab

design_wdmcr = "10.10.5.253"
design_wdmcl = "10.10.4.13"
#ledr = RTBoard.Get(IPanelLED, design_wdmcr, "/panelled")
#ledl = RTBoard.Get(IPanelLED, design_wdmcl, "/panelled")

#
# When futzing with the Unhandled Exception SmtpAppender, here's a simple way to test it
#

def testUncaught():
    logger.Log(UncaughtExceptionLogEvent(Exception("Testing.Please.Ignore: Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum")), LogLevel.ERROR)

#
# Protocol Tests
#

def SetDefaultBarcodes():
	SetReagentPlateBarcode('04012725000326307091311')
	SetSamplePlateBarcode('ABC01234')

def TestRunSamplePlate():
	DeleteInventoryData()
	ImportSS()
	SetDefaultBarcodes()
	RunSamplePlate()

#
# Barcode tests
#

def CountBarcodesSeen():
	i = 0
	if (instrument.TemplateReagentDrawer.TemplateBarcodeScanner.Barcodes.ContainsKey('SamplePlate')):
		i += 1
	else:
		print "-- Failed to find SamplePlate barcode"
	if (instrument.TemplateReagentDrawer.ReagentBarcodeScanner.Barcodes.ContainsKey('ReagentPlate0')):
		i += 1
	else:
		print "-- Failed to find inner plate barcode"
	if (instrument.TemplateReagentDrawer.ReagentBarcodeScanner.Barcodes.ContainsKey('ReagentPlate1')):
		i += 1
	else:
		print "-- Failed to find outer plate barcode"
	return i

def OpenClose():
	instrument.TemplateReagentDrawer.Open()
	instrument.TemplateReagentDrawer.Close()

def SetupScannerTest():
	instrument.TemplateReagentDrawer.ReagentAxisDrawer.RetractPreCloseVelocities = (0.008,)
	instrument.TemplateReagentDrawer.ReagentAxisDrawer.RetractPreCloseDistances = (0.165,)
	instrument.TemplateReagentDrawer.ReagentBarcodeScanner.ScanningTimeoutInMilliseconds = 59000
	instrument.TemplateReagentDrawer.TemplateBarcodeScanner.ScanningTimeoutInMilliseconds = 59000
	instrument.TemplateReagentDrawer.ReagentBarcodeScanner.TimeoutForSerialTunnelInMilliseconds = 63000
	instrument.TemplateReagentDrawer.TemplateBarcodeScanner.TimeoutForSerialTunnelInMilliseconds = 63000
	# First barcode appears at 0.165 distance from closed on a beta chassis
	# Second barcodes appear at about 0.017

def TryMultiMove():
	instrument.TemplateReagentDrawer.ReagentAxisDrawer.RetractPreCloseVelocities = (0.001, 0.04, 0.02, 0.001)
	instrument.TemplateReagentDrawer.ReagentAxisDrawer.RetractPreCloseDistances = (0.17, 0.16, 0.05, 0.03)
	instrument.TemplateReagentDrawer.ReagentAxisDrawer.RetractPreCloseCurrents = (0.7, 0.7, 0.7, 0.7)

def MultiMoveSpeed(speed):
	instrument.TemplateReagentDrawer.ReagentAxisDrawer.RetractPreCloseVelocities = (speed, 0.04, 0.02, speed,)

def ScannerStatsMoveSteps():
	TryMultiMove()

def ScannerStatsMoveSpeeds(speed):
	MultiMoveSpeed(speed)

def ScannerStats():
	SetupScannerTest()
	ScannerStatsMoveSteps()
	results = {}
	speed = 0.005	# 0.005 seems to be the minimum for this axis
	iteration = 0
	while (iteration < 1):
		ScannerStatsMoveSpeeds(speed)
		attempts = 0
		success = 0
		while (attempts < 42):
			OpenClose()
			success += CountBarcodesSeen()
			attempts += 3
		results[str(speed)] = str(float(success)/float(attempts))
		for x,y in results.iteritems():
			print x + " was " + y
		iteration += 1
		speed += 0.001

def ScannerTest():
	attempts = 0
	success = 0
	while(1):
		OpenClose()
		success += CountBarcodesSeen()
		attempts += 3
		print "timeouts left: " + str(instrument.TemplateReagentDrawer.ReagentBarcodeScanner.TimeoutForSerialTunnelInMilliseconds) + " : " + str(instrument.TemplateReagentDrawer.ReagentBarcodeScanner.ScanningTimeoutInMilliseconds)
		print "timeouts right: " + str(instrument.TemplateReagentDrawer.TemplateBarcodeScanner.TimeoutForSerialTunnelInMilliseconds) + " : " + str(instrument.TemplateReagentDrawer.TemplateBarcodeScanner.ScanningTimeoutInMilliseconds)
		print "finished retract with distance: " +  str(instrument.TemplateReagentDrawer.ReagentAxisDrawer.RetractPreCloseDistances)
		print "and velocity: " + str(instrument.TemplateReagentDrawer.ReagentAxisDrawer.RetractPreCloseVelocities)
		print "success percentage so far: " + str(float(success)/float(attempts))

# Beta6 stress tests

def PressChipsButton():
	instrument.Panel.SimulateChipsDrawerButton()

def PressSampleButton():
	instrument.Panel.SimulateTemplateDrawerButton()

def RandomPress():
	time.sleep(random.uniform(0,3))
	if (random.uniform(-1,1) > 0):
		PressChipsButton()
	else:
		PressSampleButton()

def RandomAbort():
	time.sleep(random.uniform(0,3))
	if (random.uniform(-1,1) > 0):
		instrument.InstrumentLoading.TemplateReagentDrawer.ReagentAxisDrawer.Axis.Abort()
	else:
		instrument.InstrumentLoading.ChipsTipsDrawer.ChipTipAxisDrawer.Axis.Abort()

def DrawerStress(rate):
	while True:
		PacBio.Common.Threading.ThreadUtils.Start(System.Threading.ThreadStart(RandomPress), "DrawerTestThread")
		PacBio.Common.Threading.ThreadUtils.Start(System.Threading.ThreadStart(RandomAbort), "DrawerAbortThread")
		time.sleep(random.uniform(rate - 1, rate + 1))

def DrawerStressWithoutAborts(rate):
	while True:
		PacBio.Common.Threading.ThreadUtils.Start(System.Threading.ThreadStart(RandomPress), "DrawerTestThread")
		time.sleep(random.uniform(rate - 1, rate + 1))

# IEC pressure stress tests

def TestLocal(rate):
 adc = RTBoard.Get(IADC, "10.10.4.96", "/adc")
 channel0 = ADCChannel(adc, "adc_3_100", 0) # cc
 channel3 = ADCChannel(adc, "adc_3_100", 3) # low
 channel4 = ADCChannel(adc, "adc_3_100", 4) # high
 def ChannelRead(channel, reading, expected):
  if (reading > (expected + 0.1)):
   print "transient channel " + channel + " of " + str(reading)
  if (reading < (expected - 0.1)):
   print "transient channel " + channel + " of " + str(reading)
 def Read0():
  while True:
   time.sleep(random.uniform(rate - 1, rate + 1))
   ChannelRead(0, channel0.Value, 2.0)
 def Read3():
  while True:
   time.sleep(random.uniform(rate - 1, rate + 1))
   ChannelRead(3, channel3.Value, 1.54)
 def Read4():
  while True:
   time.sleep(random.uniform(rate - 1, rate + 1))
   ChannelRead(4, channel4.Value, 3.2)
 PacBio.Common.Threading.ThreadUtils.Start(System.Threading.ThreadStart(Read0), "Read channel 0")
 PacBio.Common.Threading.ThreadUtils.Start(System.Threading.ThreadStart(Read3), "Read channel 3")
 PacBio.Common.Threading.ThreadUtils.Start(System.Threading.ThreadStart(Read4), "Read channel 4")
 PacBio.Common.Threading.ThreadUtils.Start(System.Threading.ThreadStart(Read0), "Read channel 0-1")
 PacBio.Common.Threading.ThreadUtils.Start(System.Threading.ThreadStart(Read3), "Read channel 3-1")
 PacBio.Common.Threading.ThreadUtils.Start(System.Threading.ThreadStart(Read4), "Read channel 4-1")
 PacBio.Common.Threading.ThreadUtils.Start(System.Threading.ThreadStart(Read0), "Read channel 0-2")
 PacBio.Common.Threading.ThreadUtils.Start(System.Threading.ThreadStart(Read3), "Read channel 3-2")
 PacBio.Common.Threading.ThreadUtils.Start(System.Threading.ThreadStart(Read4), "Read channel 4-2")

# IEC Test Cabinet in the lab

#iec_cabinet = "10.10.7.104"
#gpiogroup = RTBoard.Get(IGPIO, iec_cabinet, "/gpio")
#adcgroup = RTBoard.Get(IADC, iec_cabinet, "/adc")

ion_pressure_sensor = None
ion_ionizer_valve_pin = None
ion_check_valve_pin = None
ion_air_pump_pin = None
ion_discharge_start_pin = None
ion_reset_pin = None
ion_power_pin = None
ion_error_pin = None
ion_maintenance_pin = None
ion_discharging_pin = None

# Podium fan futzing

ports = System.IO.Ports.SerialPort.GetPortNames()

def findPortOffset(name):
	i = 0
	while i < len(ports):
		if (ports[i] == name):
			return i
		i+=1
	if i >= len(ports):
		return -1
	return i

def getSerialDevice(name):
	offset = findPortOffset(name)
	if (offset >= 0):
		try:
			return SerialDevice.GetDevice(offset, 115200)
		except:
			print "error opening port"
	else:
		print "port not found"

def toAppmode(device):
	# first determine if we're in the boot loader
	device.Write("?")
	try:
		response = device.Read(1, 1000)
	except:
		print "no response from board, turned on?"
		return
	device.Write("a")
	try:
		response = device.Read(1, 1000)
	except:
		print "no response from board, turned on?"
		return
	if (response == "Y"):
		# oh, we're in the boot loader, tell the board to continue to app mode
		# in app mode that would have returned ??? which we would see as ?
		device.Write('E')
		device.Read(1,1000)
		time.sleep(2)
	return device

def outputStatus(device):
	device.Write("J?")
	response = device.Read("", "?", 5000)
	print response

def testFanBoard():
	fanboard = getSerialDevice("COM4")
	toAppmode(fanboard)
	outputStatus(fanboard)
	return fanboard

# Baffle tests
# Kevin's IEC board: IP 10.10.7.149
# Milhouse instrument IEC board: (local network connection, see wiki for IP)

kevin_iec = "10.10.6.141"
#baffleaxis = RTBoard.Get(IVectorAxis, kevin_iec, "/baffle.stepper.axis")
#baffleaxis = RTBoard.Get(IVectorAxis, iec_cabinet, "/baffle.stepper.axis")

def MakeBaffle(h):
	#h = instrument.IECBoard
	if h==None:
		x = VectorAxisSvc(SimVectorAxis(1))
	else:
		x = RTBoard.Get(IVectorAxis, h, "/baffle1.stepper.axis")
	
	a = x.Actuator
	a.IdleCurrent = (0.1,)
	a.MoveCurrent = (0.2,)
	
	b = Baffle()
	b.VectorAxis = x
	b.Initialize()
	return b

def BaffleFindIndex(h):
	x = RTBoard.Get(IVectorAxis, h, "/baffle1.stepper.axis")
	w = VectorAxisWrapper(x)
	e = w.Encoder
	w.BeginMove(MoveType.Relative, 1.0)
	e.IndexCaptureEnabled = 0
	e.IndexCaptureEnabled = 1
	w.BeginMove(MoveType.Relative, -1.0)
	if (e.IndexCaptured):
		print "Found the index"
	else:
		print "Failed to find the index"

def BaffleFindIndexRT(h):
	x = RTBoard.Get(IVectorAxis, h, "/baffle1.stepper.axis")
	w = VectorAxisWrapper(x)
	e = w.Encoder
	w.Enabled = 1
	w.FindIndex()

# Ionizer mockup in python

def SetupIonizer():
	ion_pressure_sensor = ADCChannel(adcgroup, "adc_3_100", 5)	# channel 5 should be "adc_press_out6"
	ion_ionizer_valve_pin = GPIOPin(gpiogroup, "sol4_en")	# crap, humidifier is there... moving from JP7/sol3_en to JP8/sol4_en
	ion_check_valve_pin = GPIOPin(gpiogroup, "sol7_en")		# currently connected to JP11
	ion_air_pump_pin = GPIOPin(gpiogroup, "sol8_en")		# currently connected to JP12
	ion_discharge_start_pin =  GPIOPin(gpiogroup, "ion_disch_start")	# to turn it on fully
	ion_reset_pin =  GPIOPin(gpiogroup, "ion_rst")			# to reset alarms
	ion_power_pin = GPIOPin(gpiogroup, "ion_pwr_on")		# to turn on power, though it seems like it is always on anyway
	ion_error_pin = GPIOPin(gpiogroup, "ion_err")				# (alarm) if it failed
	ion_maintenance_pin = GPIOPin(gpiogroup, "ion_maintenance")	# (alarm) if it needs maintenance
	ion_discharging_pin = GPIOPin(gpiogroup, "ion_discharge")	# (alarm) if it is actually discharging
	ion_check_valve_pin.IsInput = 0
	ion_ionizer_valve_pin.IsInput = 0
	ion_air_pump_pin.IsInput = 0
	ion_power_pin.IsInput = 0
	ion_discharge_start_pin.IsInput = 0

def IonizerAlarms():
	alarmed = 0
	if (ion_error_pin.Value > 0):
		print "Ionizer has a fatal error alarm"
		alarmed = 1
	if (ion_maintenance_pin.Value > 0):
		print "Ionizer has a maintenance alarm"
		alarmed = 1
	if (alarmed == 0):
		print "No ionizer alarms"

def ClearIonizerAlarms():
	ion_reset_pin.Value = 1
	time.sleep(1)
	ion_reset_pin.Value = 0
	IonizerAlarms()

def ChargeIonizer():
	ion_check_valve_pin.Value = 1		# closed is 1 for this valve (meaning don't vent to atmosphere, set to 1 supposed to open)
	ion_ionizer_valve_pin.Value = 0		# closed is 0 for this valve (meaning don't vent to ionizer)
	ion_air_pump_pin.Value = 1			# turn on pump
	# 
	# loop for 60 seconds
	for i in range(60):
		reading = ion_pressure_sensor.Value		# how much pressure do we have?
		print i, reading
		if (reading > 3.4):
			continue;	# skip bogus high values from IADC because of race condition (bug #6096)
		if (reading > 2.8):
			print "charged"
			break;		# we're done 
		time.sleep(1)
	if (ion_pressure_sensor.Value < 2.7):
		print "i think, maybe we timed out or something"
	ion_air_pump_pin.Value = 0			# turn off pump but hold pressure
	ion_check_valve_pin.Value = 0		# relieve pump back pressure

def DischargeIonizer():
	print "discharging"
	ion_power_pin.Value = 1				# turn on ionizer power
	ion_discharge_start_pin.Value = 1	# turn on ionizer ions
	time.sleep(1)						# let that settle
	ion_ionizer_valve_pin.Value = 1		# open ionizer valve
	time.sleep(8)						# let all the air dispel
	ion_power_pin.Value = 0				# turn the power off
	ion_discharge_start_pin.Value = 0
	print "done"

def CurrentPressure():
	print ion_pressure_sensor.Value

def ResetIonizer():
	ion_check_valve_pin.Value = 0		# meaning release any stored pressure in front of pump
	ion_ionizer_valve_pin.Value = 1		# meaning release any stored pressure in canister
	ion_air_pump_pin.Value = 0
	ion_power_pin.Value = 0
	ion_discharge_start_pin.Value = 0

#### composition of ionizer testing

def ComposeIonizer():
	ion = Ionizer()
	
	gpiogroup = RTBoard.Get(IGPIO, iec_cabinet, "/gpio")
	adcgroup = RTBoard.Get(IADC, iec_cabinet, "/adc")
	
	ion_pressure_sensor = ADCChannel(adcgroup, "adc_3_100", 5)	# channel 5 should be "adc_press_out6"
	ion_ionizer_valve_pin = GPIOPin(gpiogroup, "sol4_en")	# humidifier temp; moving from JP7/sol3_en to JP8/sol4_en
	ion_check_valve_pin = GPIOPin(gpiogroup, "sol7_en")		# currently connected to JP11
	ion_air_pump_pin = GPIOPin(gpiogroup, "sol8_en")		# currently connected to JP12
	ion_discharge_start_pin =  GPIOPin(gpiogroup, "ion_discharge")
	ion_reset_pin =  GPIOPin(gpiogroup, "ion_rst")
	ion_power_pin = GPIOPin(gpiogroup, "ion_pwr_on")
	ion_error_pin = GPIOPin(gpiogroup, "ion_err")
	ion_maintenance_pin = GPIOPin(gpiogroup, "ion_maintenance")
	ion_discharging_pin = GPIOPin(gpiogroup, "ion_discharge")
	
	ion_check_valve_pin.IsInput = 0
	ion_ionizer_valve_pin.IsInput = 0
	ion_air_pump_pin.IsInput = 0
	ion_power_pin.IsInput = 0
	ion_discharge_start_pin.IsInput = 0
	
	ion.CheckValve = ion_check_valve_pin
	ion.IonizerValve = ion_ionizer_valve_pin
	ion.AirPump = ion_air_pump_pin
	ion.IonPower = ion_power_pin
	ion.IonDischarge = ion_discharge_start_pin
	ion.IonDischargingStatus = ion_discharging_pin
	ion.IonErrorStatus = ion_error_pin
	ion.IonMaintenanceStatus = ion_maintenance_pin
	ion.AirPressure = ion_pressure_sensor
	
	return ion

#### Front Panel class tests

def GreenSolid():
	instrument.Panel.GreenStatus = LedMode.Solid

#### Status board test

green_led = "pan4_led2"
yellow_led = "pan4_led1"
red_led = "pan4_led3"

#### Led tests directly to my board

test_led = "pan1_led1"

def LEDReset():
	# turn off, no blink, max intensity, max current
	led.SetLitState(test_led, 0)
	led.SetBlinking(test_led, 0, 0)
	led.SetIntensity(test_led, 255)
	led.SetMaxCurrent(test_led, 65535)
	
def LEDOn():
	led.SetLitState(test_led, 1)
	
def LEDOnLow():
	# turn it on but with no intensity (for fading in)
	led.SetIntensity(test_led, 0)
	led.SetLitState(test_led, 1)

def LEDOff():
	led.SetLitState(test_led, 0)

def LEDFadeOut():
	led.SetMaxCurrent(test_led, 65535)
	led.SetIntensityOverTime(test_led, 0, 3.0)

def LEDFadeIn():
	led.SetMaxCurrent(test_led, 65535)
	led.SetIntensityOverTime(test_led, 255, 3.0)

def LEDCycle1():
	print "slow 2.5 second cycle, 20-120 intensity, max current"
	LEDReset()
	LEDOnLow()
	led.CycleIntensityBetween(test_led, 20, 120, 5.0, 1)

def LEDCycle2():
	print "slow 2 second cycle, 0-40 intensity, max current"
	LEDReset()
	LEDOnLow()
	led.CycleIntensityBetween(test_led, 0, 40, 4.0, 1)

def LEDCycle3():
	print "faster 0.5 second cycle, 20-100 intensity, max current"
	LEDReset()
	LEDOnLow()
	led.CycleIntensityBetween(test_led, 20, 100, 1.0, 1)

def LEDCycle(speed, bottom, top):
	print str(speed) + " second cycle, " + str(bottom) + "-" + str(top) + " intensity, max current"
	LEDReset()
	LEDOnLow()
	led.CycleIntensityBetween(test_led, bottom, top, speed, 1)

def LEDCycleFull():
	print "slower 3 second cycle, 0-255 intensity, max current"
	LEDReset()
	LEDOnLow()
	led.CycleIntensityBetween(test_led, 0, 255, 6.0, 1)

### the following were for random tests, not generally useful

def LEDPulseTestFromHomer():
	# does an intensity cycle manually from homer, but hiccups
	led.SetMaxCurrent(test_led, 65535)
	led.SetBlinking(test_led, 0, 0)
	led.SetLitState(test_led, 1)
	# vary the intensity from 0 to 240 and do this back and forth a few times
	# seems to look good if we go fast enough and fade in and out in certain voltage
	# ranges.
	pacing = 0.025	# 40 times per second
	for j in range(0,9):
		print "loop iteration " + str(j)
		for i in range(0, 20):
			new_intensity = i * 12;
			led.SetIntensity(test_led, new_intensity)
			time.sleep(pacing)
		for k in range(20, 0, -1):
			new_intensity = k * 12;
			led.SetIntensity(test_led, new_intensity)
			time.sleep(pacing)

def LEDCPULoadTest():
	for i in range(0, 8):
		channel_var = "channel" + str(i)
		print "cycling led " + channel_var
		led.SetLitState("channel" + str(i), 1)
		led.SetMaxCurrent("channel" + str(i), 65535)
		led.SetBlinking("channel" + str(i), 0, 0)
		led.SetIntensity("channel" + str(i), 120)
		led.CycleIntensityBetween("channel" + str(i), 20, 80, 5.0, 1)

def LEDMiniRave():
	# max intensity, 0.5hz blink by fpga, max current
	LEDReset()
	led.SetBlinking(test_led, 1, 1)
	led.SetLitState(test_led, 1)