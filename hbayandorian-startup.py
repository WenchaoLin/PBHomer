# hovig's standard homer debug environment

# ralph aug 5
# --gui --cfg XRealRobotBoard=10.10.4.85 --cfg StageBoard=10.10.4.70 --cfg OpticsBoard-532=10.10.6.252 --cfg OpticsBoard-642=10.10.6.222  --cfg OttoServiceAddress=mp-nrt04:8082
# ralph july 29
# --gui --cfg XRealRobotBoard=10.10.4.85 --cfg XOpticsBoard-532=10.10.6.252  --cfg StageBoard=10.10.4.70 --cfg OttoServiceAddress=mp-nrt04:8082

# ralph july 28
# --gui --cfg XRealRobotBoard=10.10.4.85 --cfg XOpticsBoard-532=10.10.6.252  --cfg StageBoard=10.10.4.70 --cfg OttoServiceAddress=mp-nrt04:8082

# ralph july 24
# --gui --cfg XRealRobotBoard=10.10.4.85 --cfg OpticsBoard-532=10.10.6.252  --cfg StageBoard=10.10.4.70 --cfg OttoServiceAddress=mp-nrt04:8082


# ralph
# --gui --cfg StageBoard=10.10.4.70

# july 22 mingan
# --gui --cfg XRealRobotBoard=10.10.4.85 --cfg XOpticsBoard-532=10.10.6.238 --cfg StageBoard=10.10.6.173 --cfg OttoServiceAddress=mp-nrt04:8082 --cfg OpticsBoard-642=10.10.6.254

# stage/objective/camera command line options:
# --cfg XRealRobotBoard=10.10.4.85 --cfg XOpticsBoard-532=10.10.6.238 --cfg StageBoard=10.10.6.173 --cfg OttoServiceAddress=mp-nrt04:8082

import clr

import random
from System import *
from System.Collections import *
from System.Collections.Generic import *
from System.Drawing import *
from PacBio.Common.Numeric import *
from PacBio.Instrument.Camera import *
from PacBio.Instrument.Alignment import *
from PacBio.Instrument.Alignment.Test import *
from PacBio.Instrument.Interfaces.Movement import *
from PacBio.Common.IO import *
from PacBio.Instrument.Halcon import *
from PacBio.Instrument.Chip import *
from HalconDotNet import *

#focalROI = ROIUtil.RectangularGrid(20, 20, qdc.GrabRect)
#rfm = RegionFocalMeasure(focalROI)
#stackTrajectory = TrajectoryUtil.LinearTrajectory((0, 0, -50e-6, 0, 0, 0), (0, 0, 50e-6, 0, 0, 0), 20)

#sl = StageLeveler(qdc, instrument.Stage)

#qdc = QuickAndDirtyDataCameraSimulator("S:\\Software\\HovigTest\\layout\\chiplayout.xml", instrument, 2584, 2160)

#stackTrajectory = TrajectoryUtil.LinearTrajectory((0, 0, -50e-6, 0, 0, 0), (0, 0, 50e-6, 0, 0, 0), 20)

#sl = StageLeveler(qdc, instrument.Stage)

#sl = SimpleStageLeveler(qdc, instrument.Stage)

# naming convention:
# first character: c/s calibration/sequencing chip
# if second character is d then distorted, if the second character is n then not distorted
# ends with L16, L24, or L31 (indicates pane?)
# this is pretty temporary

# this really ought to go into the database
##### TEMP FIX FOR 4375
#stage.coarseAxisControls.EnableAll = False
#cmv = stage.CoarseAxisControls.MaxVel
#v = cmv[0]/4.0
#v = 0.003 # "normal" max speed is 0.012
#stage.coarseAxisControls.MaxVel = (v, v, v, v, v, v)
#stage.coarseAxisControls.EnableAll = True
#### END TEMP FIX

layoutFilenames = {
    "cnL16": "SpringfieldPANE_L16_L00_L31_L32_LOOK2_DISTD_NN_TYPE_CALIB.xml.gz",
    "snL16": "SpringfieldPANE_L16_L00_L31_L32_LOOK2_DISTD_NN_TYPE_SEQUE.xml.gz",
    "cdL16": "SpringfieldPANE_L16_L00_L31_L32_LOOK2_DISTD_YY_TYPE_CALIB.xml.gz",
    "sdL16": "SpringfieldPANE_L16_L00_L31_L32_LOOK2_DISTD_YY_TYPE_SEQUE.xml.gz",
    "snL24": "SpringfieldPANE_L24_L00_L31_L32_LOOK2_DISTD_NN_TYPE_SEQUE.xml.gz",
    "sdL24": "SpringfieldPANE_L24_L00_L31_L32_LOOK2_DISTD_YY_TYPE_SEQUE.xml.gz",
    "cnL31": "SpringfieldPANE_L31_L00_L31_L32_LOOK2_DISTD_NN_TYPE_CALIB.xml.gz"
}

# there are seven springfield 2.0 layouts
# layoutFolder = "S:\\Software\\HovigTest\\layout\\"
layoutFolder = "c:\\layouts\\"
layoutName = "sdL24"

def layoutFile(layoutName):
    return layoutFolder + layoutFilenames[layoutName]

def makeqdc():
    print "Loading chip layout..."
    qdc = QuickAndDirtyDataCameraSimulator(layoutFile(layoutName), instrument)
    print "Done loading chip layout"
    return qdc
    
def makeqdr():
    print "Creating regions of interest provider..."
    qdr = QuickAndDirtyROIProvider(layoutFile(layoutName), instrument)
    print "Done"
    return qdr

def getbadcentroidrois(centroids):
    # if the center of a centroid is exactly (0.0, 0.0), that is a strong indicator of a bug somewhere
    badcentroidrois = []
    for centroid in centroids:
         if(centroid.Center.X < 1e-7 and centroid.Center.Y < 1e-7):
            badcentroidrois.append(centroid.RegionOfInterest)
    return badcentroidrois

def makesimstuff():
    global qdr, r, qdc, frame, cra, xycm, tr, rtr, centroider, centroids, badcentroidrois
    qdr = makeqdr() # provides regions for analysis
    r = qdr.GetRegions(-1, 2) # get regions for all looks
    qdc = makeqdc() # provides frame
    frame = qdc.Snapshot(True) # frame to be analzed
    cra = CoarseRegistrationAnalyzer() # performs coarse registration
    xycm = cra.Analyze(frame) # store coarse registration
    tr = xycm.Apply(r) # move regions to match coarse registration
    rtr = ROIUtil.InRange(tr, frame) # remove regions which are outside the image
    centroider = CentroidRegionAnalyzer(rtr) # for calculating centroid stuff
    centroids = centroider.Analyze(frame) # calculate centroid stuff
    badcentroidrois = getbadcentroidrois(centroids) #get bad centroids

#def testbffo():
#    trajectory = TrajectoryUtil.LinearTrajectory((0, 0, 100e-6, 0, 0, 0), (0, 0, 180e-6, 0, 0, 0), 20)
#    bffo = BruteForceFocusOptimizer(camera, stage.Axis, trajectory)
#    bffo.Optimize()
#    z = bffo.Stacker.ResultSelector.Position(2)
#    f = bffo.ObjectiveValues
#    sp = SimplePlot()
#    sp.AddPlotData(z, f)
#    sp.Plot()

def testbffoqdc(): # test brute force focus optimizer
    trajectory = TrajectoryUtil.LinearTrajectory((0, 0, -50e-6, 0, 0, 0), (0, 0, 50e-6, 0, 0, 0), 19)
    bffo = BruteForceFocusOptimizer(qdc, stage.Axis, trajectory)
    bffo.Optimize()
    view(bffo.ObjectiveValues)

def moveZ(dest):
    print "Setting Z", dest
    z.TargetPosition = dest
    z.WaitForMove()

def testZ(z):
    for i in range(-4, 4):
        moveZ(z + i * 100e-6)
    
def stressZ():
    stage.Axis.FindIndex()
    stage.Axis.WaitForMove()
    zv = z.CurrentPosition
    for i in range(1, 100):
        testZ(zv)
#old
#def viewCam():
#    stage.Axis.FindIndex()
    # camera settings
#    camera.Exposure = 0.01
#    camera.PollInterval = 1
#    camera.StartPreviewImaging()
#    view(camera)
    
def randomstagepos():
    x = random.uniform(-500e-6, 500e-6)
    y = random.uniform(-500e-6, 500e-6)
    z = random.uniform(-500e-6, 500e-6)
    a = random.uniform(-10e-3, 10e-3)
    b = random.uniform(-10e-3, 10e-3)
    c = random.uniform(-10e-3, 10e-3)
    return XYZabc(x, y, z, a, b, c)
    
def randomleglengths():
    l1 = random.uniform(-1000e-6, 1000e-6)
    l2 = random.uniform(-1000e-6, 1000e-6)
    l3 = random.uniform(-1000e-6, 1000e-6)
    l4 = random.uniform(-1000e-6, 1000e-6)
    l5 = random.uniform(-1000e-6, 1000e-6)
    l6 = random.uniform(-1000e-6, 1000e-6)
    return (l1, l2, l3, l4, l5, l6)

def coarseaxismovetest():
    coarse = stage.CoarseAxis
    enc = stage.Encoder
    target = randomleglengths()
    coarse.BeginMove(MoveType.Absolute, target)
    coarse.WaitForMove()
    dest = enc.CurrentPosition
    print "test position: " + str(target)
    print "dest position: " + str(dest)
    diff = XYZabc(target) - XYZabc(dest)
    print "###DIFF POSITION: " + str(diff)
    print "###DIFF 3legs1:   " + str(diff.XYZ.Length)
    print "###DIFF 3legs2:   " + str(diff.abc.Length)

def viewCam():
    # Init the stage
    stage.Axis.FindIndex()
    
    #illum.Brightness = 0.3
    #illum.Enabled = True
        
    # camera.GrabRect = Rectangle(0, 0, 512, 512) # For preview speed
    camera.Exposure = 0.1
    camera.PollInterval = 0.5 # seconds
    view(camera)
    z.TargetPosition = 140e-6   # A good initial Z

def stagemovetest():
    testPosition = randomstagepos()
    stage.Axis.TargetPosition = testPosition
    stage.Axis.WaitForMove()
    destPosition = XYZabc(stage.Axis.CurrentPosition)
    diff = destPosition - testPosition
    print "test position: " + str(testPosition)
    print "dest position: " + str(destPosition)
    print "error XYZ: " + str(diff.XYZ.Length) + " error abc: " + str(diff.abc.Length)
    

def stacktest():
    imageSrc = CameraDataSource(camera)
    rois = ROIUtil.RectangularGrid(20, 20, camera.GrabRect)
    rfa = RegionFocalAnalyzer(rois)
    global imageStacker
    imageStacker = ImageStacker[IRegionStatisticAnalysis](stage.Axis, imageSrc, rfa)

def lmatest():
    lma  = LocalMaximaAnalyzer()
    points = lma.Analyze(qdc.Snapshot(True))
    rois = ROIUtil.FromPoints(points, 1.3)
    insiderois = ROIUtil.InRange(rois, frame, 30.0)
    cra = CentroidRegionAnalyzer(insiderois)
    result = cra.Analyze(frame)
    sp = SimplePlot()
    intensities = []
    for i in range(0, len(result)-1):
        intensities.append(result[i].Centroid.Intensity)
    hi = Histogram(intensities)
    sp.Plot2D[Double](hi.BinMin, hi.BinFraction)
    sigmas = []
    for i in range(0, len(result)-1):
        sigmas.append(result[i].Centroid.Sigma)
    hs = Histogram(sigmas)
    sp.Plot2D[Double](hs.BinMin, hs.BinFraction)
    centroiddisagreement = []
    for i in range(0, len(result) - 1):
    	centroiddisagreement.append((result[i].Centroid.Center - insiderois[i].Representative).Length())
    hc = Histogram(centroiddisagreement)
    sp.Plot2D[Double](hc.BinMin, hc.BinFraction)
    
def quicktestquiver():
    lma  = LocalMaximaAnalyzer()
    points = lma.Analyze(qdc.Snapshot(True))
    rois = ROIUtil.FromPoints(points, 1.3)
    insiderois = ROIUtil.InRange(rois, frame, 30.0)
    cra = CentroidRegionAnalyzer(insiderois)
    result = cra.Analyze(frame)
    sp = SimplePlot()
    pointx = []
    pointy = []
    centroidoffsetx = []
    centroidoffsety = []
    for i in range(0, len(result) - 1):
        pointx.append(insiderois[i].Representative.X)
        pointy.append(insiderois[i].Representative.Y)
    	centroidoffsetx.append(100*(result[i].Centroid.Center - insiderois[i].Representative).X)
    	centroidoffsety.append(100*(result[i].Centroid.Center - insiderois[i].Representative).Y)
    sp.PlotVectorField[Double](pointx, pointy, centroidoffsetx, centroidoffsety)
    
def testbeamletstack1d():
    global lma, points, rois, insiderois, bs
    lma  = LocalMaximaAnalyzer()
    points = lma.Analyze(qdc.Snapshot(True))
    rois = ROIUtil.FromPoints(points, 1.3)
    insiderois = ROIUtil.InRange(rois, frame, 30.0)
    goodrois = []
    for i  in range(0,1000):
	    goodrois.append(insiderois[i]) 
    bs = BeamletStacker1D(stage.Axis, qdc)
    bs.Initialize()
    bs.RegionsOfInterest = goodrois
    bs.StartPoint = (0.0, 0, 0, 0, 0, 0)
    bs.EndPoint = (10e-6, 0.0, 0, 0, 0, 0)
    bs.NumberOfSteps = 10
    

#camera = instrument.CollectionPath[433].Camera
camera = instrument.CollectionPath[538].Camera

#z = VectorAxisWrapper(stage.Axis, 2)
#view(z)

#illum = instrument.Illuminator
#illum1 = illum.Target.Channels[0].Illuminator

sl = instrument.Children["stageLeveler"]

# makesimstuff()


# a very simple csv-writing script
def writecsv(csvfilename, header, data):
	f = open(csvfilename, 'w')
	headertext = [str(e) for e in header]
	f.write(','.join(headertext) + '\n')
	for row in data:
		rowtext = [str(e) for e in row]
		f.write(','.join(rowtext) + '\n')
	f.close()
	
from PacBio.Instrument.Alignment.Analyzers import *
import random

def testdcra(csvfilename, camera, xrange, yrange, thetarange, num):
    dcra = DataCameraRegistrationAnalyzer()
    stage.AutoAxis = True
    initialpos = XYZabc(stage.Axis.CurrentPosition)
    header = ['dcra_x', 'dcra_y', 'dcra_theta', 'sx', 'sy', 'sz', 'sa', 'sb', 'sc']
    data = []
    random.seed(42)
    for i in range(0,num):
	    newx = random.uniform(-xrange, xrange)
	    newy = random.uniform(-yrange, yrange)
	    newtheta = random.uniform(-thetarange, thetarange)
	    stage.Axis.TargetPosition = XYZabc(newx, newy, initialpos.Z, initialpos.a, initialpos.b, newtheta)
	    stage.Axis.WaitForMove()
	    sp = stage.Axis.CurrentPosition
	    frame = camera.Snapshot(True)
	    xycm = dcra.Analyze(frame)
	    data.append([xycm[0], xycm[1], xycm[2], sp[0], sp[1], sp[2], sp[3], sp[4], sp[5]])
    writecsv(csvfilename, header, data)
    

def testcc(csvfilename, cc, xrange, yrange, thetarange, num):
    initialpos = XYZabc(stage.Axis.CurrentPosition)
    header = ['dcra_x', 'dcra_y', 'dcra_theta', 'sx', 'sy', 'sz', 'sa', 'sb', 'sc']
    data = []
    random.seed(42)
    for i in range(0,num):
	    newx = random.uniform(-xrange, xrange)
	    newy = random.uniform(-yrange, yrange)
	    newtheta = random.uniform(-thetarange, thetarange)
	    stage.Axis.TargetPosition = XYZabc(newx, newy, initialpos.Z, initialpos.a, initialpos.b, newtheta)
	    stage.Axis.WaitForMove()
	    sp = stage.Axis.CurrentPosition
	    xycm = cc.ChipPosition
	    data.append([xycm[0], xycm[1], xycm[2], sp[0], sp[1], sp[2], sp[3], sp[4], sp[5]])
    writecsv(csvfilename, header, data)