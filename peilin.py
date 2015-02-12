from CameraSetUtils import *
from AcquisitionUtils import *
from AlignmentUtils import *
from PacBio.Common.Movie import *
from collectMovies import *
from protocols import *
from PacBio.Common.Node import NodeInfo
from PacBio.Instrument.Interfaces import *
from PacBio.Instrument.Analysis.Pipeline import *
import time
import datetime
from System import TimeSpan

#-----------
# Check time to grab a frame
#-----------

def frameRate(cam,numFrames):
    print System.DateTime.Now
    for i in range(0, numFrames):
         cam.Snapshot(True)
    print System.DateTime.Now
    

#-----------
# Add some custom offset ROIs for movie-to-trace testing
#-----------

c50k_circle_zmw_roi = ZmwROI(type = ROIType.ZMWCIRC, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 126.0, y = 126.0))
c55k_circle_zmw_roi = ZmwROI(type = ROIType.ZMWCIRC, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 132.0, y = 132.0))
c60k_circle_zmw_roi = ZmwROI(type = ROIType.ZMWCIRC, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 138.0, y = 138.0))

c35K_zmw_roi = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 94.0, y = 94.0))
c40K_zmw_roi = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 100.0, y = 100.0))
c50K_zmw_roi = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 111.0, y = 111.0))
c55K_zmw_roi = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 117.0, y = 117.0))
c60K_zmw_roi = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 122.0, y = 122.0))
c70K_zmw_roi = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 132.0, y = 132.0))

c5K_zmw_roi_posx_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 75.0, y = 0.0), extent = Float2D(x = 35.0, y = 35.0))
c5K_zmw_roi_negx_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = -75.0, y = 0.0), extent = Float2D(x = 35.0, y = 35.0))
c5K_zmw_roi_posy_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = 75.0), extent = Float2D(x = 35.0, y = 35.0))
c5K_zmw_roi_negy_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = -75.0), extent = Float2D(x = 35.0, y = 35.0))

c25K_zmw_roi_posx_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 75.0, y = 0.0), extent = Float2D(x = 79.0, y = 79.0))
c25K_zmw_roi_negx_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = -75.0, y = 0.0), extent = Float2D(x = 79.0, y = 79.0))
c25K_zmw_roi_posy_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = 75.0), extent = Float2D(x = 79.0, y = 79.0))
c25K_zmw_roi_negy_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = -75.0), extent = Float2D(x = 79.0, y = 79.0))
c30K_zmw_roi_posx_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 75.0, y = 0.0), extent = Float2D(x = 86.0, y = 86.0))
c35K_zmw_roi_posx_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 75.0, y = 0.0), extent = Float2D(x = 94.0, y = 94.0))
c40K_zmw_roi_posx_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 75.0, y = 0.0), extent = Float2D(x = 100.0, y = 100.0))
c50K_zmw_roi_posx_offset  = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 30.0, y = 0.0), extent = Float2D(x = 111.0, y = 111.0))

#-----------
# Custom protocols
#-----------

def runProtoCustom(secs, exposure, label=''):
   """Run a custom 100-line strip movie, pass in SECONDS and FILENAME"""
   print 'Running custom protocol...'
   now = datetime.datetime.now()
   filename = now.strftime("%Y-%m%d-%H%M_Strip_") + label
   RunProtocolNoScan( \
      'SquatMovieOnlyProtocol.py', \
      AcquisitionTime=TimeSpan(0, 0, secs), \
      ExposureTime=exposure, \
      NeedTiFrames=True, \
      NeedLaserIllum=True, \
      NeedPostMovieTi=True, \
      NeedTraceExtraction=False,\
      UseMaxFrameSize=False, \
      RunType='SEQUENCING', \
      TILevel1=0.139, \
      TILevel2=0.093, \
      TILevel3=0.105, \
      TILevel4=0.085, \
      Filename=filename, \
      Stride=1, \
   )



def runCustomTrace( \
        acquisition_time, \
        exposure=0.01,
        dye_ids='20091214_A555, 20091214_A568, 20091214_A647, 20091214_Cy5p5', \
        label='', \
        chip_layout=default_chip_layout, \
        gridder_mode='REFERENCE_MCD', \
        zmw_roi=c10K_zmw_roi, \
        papFilename='' \
    ):
    '''Run a capture and extract traces'''
    print 'Running Trace Extraction'
    now = datetime.datetime.now()
    filename = now.strftime("%Y-%m%d-%H%M_Trace_") + label
    RunProtocolNoScan( \
        'SquatMovieOnlyProtocol.py', \
        NeedTiFrames=True, \
        NeedLaserIllum=True, \
        NeedTraceExtraction=True, \
        UseMaxFrameSize=False, \
        AcquisitionTime=TimeSpan(0, 0, acquisition_time), \
        ExposureTime=exposure, \
        Filename=filename, \
        PAPFilename=papFilename, \
        RunType='SEQUENCING', \
        DyeIds=dye_ids, \
        GridderMode=gridder_mode, \
        ChipLayout=chip_layout, \
	ZmwRoiType=zmw_roi_type_to_string(zmw_roi), \
        ZmwRoiOriginX=zmw_roi.center.x, \
        ZmwRoiOriginY=zmw_roi.center.y, \
        ZmwRoiExtentX=zmw_roi.extent.x, \
        ZmwRoiExtentY=zmw_roi.extent.y, \
        TILevel1=0.139, \
        TILevel2=0.093, \
        TILevel3=0.105, \
        TILevel4=0.085, \
    )


def peilinProtoWithPAP(
        acquisition_time,
        exposure=0.01,
        dye_ids='20091214_A555, 20091214_A568, 20091214_A647, 20091214_Cy5p5',
        label='',
        chip_layout=default_chip_layout,
        gridder_mode='OFF',
        zmw_roi=small_zmw_roi,
        collection_dir=''
    ):
    """Run a trace movie on Otto then process it on the PAP"""
    
    now = datetime.datetime.now()
    filename = now.strftime("%Y-%m%d-%H%M_Trace_") + label

    cluster = Cluster.Instance
    t = cluster.ReservePAP()
    papname = t[0]
    spooldir = t[1]
    papFilename = spooldir + "/" + filename
    print "Spooling to: ", papFilename
    runCustomTrace(acquisition_time, exposure, dye_ids, label, chip_layout, gridder_mode, zmw_roi, papFilename)
    
    metadataUri = UriTools.FilepathToUri(papFilename + ".metadata.xml")
    md = Metadata()
    md.InstrumentName = NodeInfo.Instance.NodeName
    if collection_dir == '':
		collection_dir = FileUtil.TempDir
    md.RunName = filename # We are currently running this without a job/run
    md.CollectionPathURI = UriTools.FilepathToUri(collection_dir).ToString()
    print "Creating job on " + papname + ", metadata in " + str(metadataUri) + ", basefiles in " + collection_dir
    job = cluster.CreateAnalysisProcess(metadataUri, md)
    # Don't wait for the movie to finish processing before the user can do
    # other stuff
    # job.Wait()


def runCustomTraceWithThumbnail( 
        acquisition_time,
        exposure=0.01, 
        doPostTi=True, 
        dye_ids='20091214_A555, 20091214_A568, 20091214_A647, 20091214_Cy5p5',
        label='', 
        chip_layout=default_chip_layout, 
        gridder_mode="REFERENCE_MCD", 
        zmw_roi=c5K_zmw_roi, 
        thumbnail_control_rect=small_thumbnail_control_rect
    ):
    '''Run a capture, extract traces, and write a thumbnail movie'''
    print "Running trace extraction"
    now = datetime.datetime.now()
    filename = now.strftime("%Y-%m%d-%H%M_TrcThumb_") + label
    RunProtocolNoScan( \
        'SquatMovieOnlyProtocol.py', \
        NeedTiFrames=True, \
        NeedLaserIllum=True, \
        NeedTraceExtraction=True, \
        NeedPostMovieTi=doPostTi, \
        ThumbnailFromZmwROI=True, \
        ThumbnailFromZmwROIControlRect=thumbnail_control_rect, \
        UseMaxFrameSize=False, \
        AcquisitionTime=TimeSpan(0, 0, acquisition_time), \
        ExposureTime=exposure, \
        Filename=filename, \
        Stride=1, \
        RunType='SEQUENCING', \
        DyeIds=dye_ids, \
        GridderMode=gridder_mode, \
        ChipLayout=chip_layout, \
        ZmwRoiType=zmw_roi_type_to_string(zmw_roi), \
        ZmwRoiOriginX=zmw_roi.center.x, \
        ZmwRoiOriginY=zmw_roi.center.y, \
        ZmwRoiExtentX=zmw_roi.extent.x, \
        ZmwRoiExtentY=zmw_roi.extent.y, \
        TILevel1=0.139, \
        TILevel2=0.093, \
        TILevel3=0.105, \
        TILevel4=0.085, \
    )
    
   
def runBL5reference(secs, exposure, label=''):
   """Run a custom 100-line strip movie, pass in SECONDS and FILENAME"""
   print 'Running custom protocol...'
   now = datetime.datetime.now()
   filename = now.strftime("%Y-%m%d-%H%M_Strip_") + label
   RunProtocolNoScan( \
      'SquatMovieOnlyProtocol.py', \
      AcquisitionTime=TimeSpan(0, 0, secs), \
      ExposureTime=exposure, \
      NeedTiFrames=True, \
      NeedLaserIllum=True, \
      NeedPostMovieTi=True, \
      NeedTraceExtraction=False,\
      UseMaxFrameSize=False, \
      RunType='SEQUENCING', \
      TILevel1=0.116, \
      TILevel2=0.091, \
      TILevel3=0.099, \
      TILevel4=0.085, \
      Filename=filename, \
      Stride=1, \
   )


#-----------
# Add a script for setting custom LUTs
#-----------

def setLUTs(low = 0, range = 256):
    "Set the LUTs for all 4 cameras"
    cam1.SetCustomIndexTable(low, range)          
    cam2.SetCustomIndexTable(low, range)          
    cam3.SetCustomIndexTable(low, range)          
    cam4.SetCustomIndexTable(low, range)
    cam1.Snapshot(True)
    cam2.Snapshot(True)
    cam3.Snapshot(True)
    cam4.Snapshot(True) 

#-----------
# Add a script for capturing illumination path and stage settings
#-----------

def getIllumData(fname):
    camb=instrument.BSBR.Camera
    #saving BSBR at acquisition settings
    instrument.BSBR.Camera.Exposure=cas.AcquiringParams.BSBRSetupParams.CamExposure
    instrument.BSBR.Illuminator.Brightness=cas.AcquiringParams.BSBRSetupParams.IRBrightness
    instrument.BSBR.Illuminator.PulseWidth=cas.AcquiringParams.BSBRSetupParams.IRPulse
    voa1.SetPower(cas.AcquiringParams.GreenLaserPower)
    voa2.SetPower(cas.AcquiringParams.RedLaserPower)
    shutter1.BeginOpen(True)
    shutter2.BeginOpen(True)
    sleep(600)
    ImageLogger.Instance.LogRaw(camb.Snapshot(True), fname+"_RefBoth_")
    #saving the red FL image
    shutter1.BeginOpen(False)
    ImageLogger.Instance.LogRaw(cam3.Snapshot(True), fname+"_RedFL_")
    sleep(600)
    #saving the green FL image
    shutter1.BeginOpen(True)
    shutter2.BeginOpen(False)
    sleep(600)
    ImageLogger.Instance.LogRaw(cam1.Snapshot(True), fname+"_GreenFL_")
    #save data after fine alignment
    shutter1.BeginOpen(False)    
    data = []
    header = []
    header.append('relay1 Mag')
    data.append(relay1.CurrentFocalLength)
    header.append('relay1 Mask')
    data.append(relay1.CurrentMaskPlane)
    header.append('relay2 Mag')
    data.append(relay2.CurrentFocalLength)
    header.append('relay2 Mask')
    data.append(relay2.CurrentMaskPlane)
    header.append('BSBR Lens')
    data.append(instrument.BSBR.Focus.CurrentPosition)
    header.append('BSBR Exp')
    data.append(instrument.BSBR.Camera.Exposure)
    header.append('BSBR IR Brightness')
    data.append(instrument.BSBR.Illuminator.Brightness)
    header.append('BSBR IR Pulsewidth')
    data.append(instrument.BSBR.Illuminator.PulseWidth)
    header.append('DOE 1')
    data.append(doe1.CurrentAngle)
    header.append('DOE 2')
    data.append(doe2.CurrentAngle)
    header.append('Stage X')
    data.append(stage.Axis.CurrentPosition[0])
    header.append('Stage Y')
    data.append(stage.Axis.CurrentPosition[1])
    header.append('Stage Z')
    data.append(stage.Axis.CurrentPosition[2])
    header.append('Stage Alpha')
    data.append(stage.Axis.CurrentPosition[3])
    header.append('Stage Beta')
    data.append(stage.Axis.CurrentPosition[4])
    header.append('Stage Theta')
    data.append(stage.Axis.CurrentPosition[5])
    header.append('Camera Exp')
    data.append(cam1.Exposure)
    csvwrite(fname+".csv",header,data)

#-----------
# Modify temp stage leveler scripts to use TI
#-----------

#temp stage leveler
#one line scripts for four Arm leveling
#Janice Cheng
#Pei-Lin edit to add TI

from IlluminationLevelUtils import *
from StageLevelUtil import *
from TIFL import *
import random
import datetime
from PacBio.Common.Utils import *
from PacBio.Common.RemotePlot import *
########## functions
def levelRep(whichCam = CameraEnum.Yellow, initPos = None, initPosEpZ = 40e-6, initNegEpZ = 40e-6, stepsPerStack = 40, maxIters = 1,selWin=False,selWinMethod=1,VCX=40,VCY=40):
    ill = instrument.Children["illuminationLeveler"]
    stageLeveler=ill.stageLeveler
    stageLeveler.Params = LevelerParams()
    stageLeveler.PeakMethod=PeakFocusPointResult.PeakMethod.GaussianOffset1D
    stageLeveler.Params.LevelingCamera = whichCam       # Blue, Green, Yellow, Red
    if not initPos:	
        initPos = XYZabc(stage.Axis.CurrentPosition)    # the "center" position of the stack
    stageLeveler.Params.InitialPosition = initPos
    stageLeveler.Params.InitialPosEpsilonZ = initPosEpZ # how far above the center of focus to stack
    stageLeveler.Params.InitialNegEpsilonZ = initNegEpZ # how far below the center of focus to stack
    stageLeveler.Params.StepsPerStack = stepsPerStack   # how many steps to use, per stack
    stageLeveler.Params.MaxIterations = maxIters        # how many iterations to use
    stageLeveler.Params.FocalControlParams.NumColumnsX=VCX
    stageLeveler.Params.FocalControlParams.NumColumnsY=VCY
    if selWin==False:
      print "MESSAGE:using Full FRAME"+" ; IterNum:"+str(stageLeveler.Params.MaxIterations)+";Range="+str(stageLeveler.Params.InitialNegEpsilonZ)
      stageLeveler.Params.FocalControlParams.FocalControlParams.FocalConstraint = FocalConstraintEnum.FullImage
    else:
      #stageLeveler.MakeCameraSelection()
      print "MESSAGE:using Selected ROIs"+"  IterNum:"+str(stageLeveler.Params.MaxIterations)+";Range="+str(stageLeveler.Params.InitialNegEpsilonZ)
      if selWinMethod==1:
        stageLeveler.Params.FocalControlParams.FocalConstraint = FocalConstraintEnum.CameraSelectionStateWhole
      else:
        stageLeveler.Params.FocalControlParams.FocalConstraint = FocalConstraintEnum.CameraSelectionStateSubdivided
    print stageLeveler.Params.FocalControlParams.FocalConstraint
    stageLeveler.Level()
    print 'initPos =', initPos
    finalPos = XYZabc(stage.Axis.CurrentPosition) # record the final position of the chip
    print 'finalPos =', finalPos
    levelError = (finalPos-initPos)*1.0e6           # calculate the error before/after chip leveling, everything in um/urad
    print "the level error in z is "+str(levelError[2])+" um"    
    print "the level error in alpha is "+str(levelError[3])+" urad"
    print "the level error in beta is "+str(levelError[4])+" urad"
    print "..."
    return levelError

def fullFOV_ph():
  ti.Enabled=True
  sleep(2000)
  instrument.Illuminator.Target.GetChannel(2).Enabled=True
  instrument.Illuminator.Target.GetChannel(2).Brightness=cas.AlignParams.StageLevelParams.TIBrightness
  levelRep(whichCam = CameraEnum.Yellow, initPos = cas.AlignParams.StageLevelParams.StartingStagePosition, initPosEpZ = 40e-6, initNegEpZ = 40e-6, stepsPerStack = 40, maxIters = 2,selWin=False)

def FourArms_ph(alpha,beta):
  ti.Enabled=True
  sleep(2000)
  instrument.Illuminator.Target.GetChannel(2).Enabled=True
  instrument.Illuminator.Target.GetChannel(2).Brightness=cas.AlignParams.StageLevelParams.TIBrightness+0.03
  levelRep(whichCam = CameraEnum.Yellow, initPos = None, initPosEpZ = 20e-6, initNegEpZ = 20e-6, stepsPerStack = 20, maxIters = 2,selWin=True)
  Offset=XYZabc(0,0,0,alpha,beta,0)
  stage.Axis.TargetPosition=XYZabc(stage.Axis.CurrentPosition)+Offset
  ti.Enabled=False
  instrument.Illuminator.Target.GetChannel(2).Brightness=0.0



