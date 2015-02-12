from CameraSetUtils import *
from AcquisitionUtils import *
from PacBio.Common.Movie import *
from PacBio.Instrument.Camera import * 
from System.Text.RegularExpressions import *
from collectMovies import *
from protocols import *
import time
import datetime
from System import TimeSpan

ti.Target.MaxTimeUnsafeBrightness=30

def captureMovie(filename = "testmovie.mov.h5", numFrames = 100, stride = 0):
    """Grab a movie with otto, default to one minute (if exposure is 10 ms), with no skipped frames"""
    gui = instrument.CameraSet.Subframe(SubframeID.GUI_PREVIEW_SUBFRAME)
    ms = instrument.CameraSet.Subframe(SubframeID.MOVIE_THUMBNAIL_SUBFRAME)
    ms.GrabRect = gui.GrabRect
    ms.Enabled = True
    instrument.CameraSet.StartMovieCapture(filename, numFrames, stride)

def frameRate(cam,numFrames):
    print System.DateTime.Now
    for i in range(0, numFrames):
         cam.Snapshot(True)
    print System.DateTime.Now

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

c5K_zmw_roi_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 75.0, y = 0.0), extent = Float2D(x = 35.0, y = 35.0))
c15K_zmw_roi_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 66.0, y = 0.0), extent = Float2D(x = 61.0, y = 61.0))
c20K_zmw_roi_offset = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 75.0, y = 0.0), extent = Float2D(x = 70.0, y = 70.0))
c20K_zmw_roi = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 70.0, y = 70.0))
c22p5K_zmw_roi = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 75.0, y = 75.0))
c25K_zmw_roi = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 79.0, y = 79.0))
c30K_zmw_roi = ZmwROI(type = ROIType.ZMWRECT, center = Float2D(x = 0.0, y = 0.0), extent = Float2D(x = 87.0, y = 87.0))

def runProtoCustom(secs, exposure, label=''):
   """Run a custom 100-line strip movie, pass in SECONDS and FILENAME"""
   print 'Running custom protocol...'
   now = datetime.datetime.now()
   filename = now.strftime("%Y-%m%d-%H%M_Strip_") + label
   RunProtocolNoScan( \
      'hotStartSanity.py', \
      AcquisitionTime=TimeSpan(0, 0, secs), \
      ExposureTime=exposure, \
      NeedTiFrames=True, \
      NeedLaserIllum=True, \
      NeedPostMovieTi=True, \
      NeedTraceExtraction=False,\
      UseMaxFrameSize=False, \
      RunType='SEQUENCING', \
      TILevel1=0.2, \
      TILevel2=0.095, \
      TILevel3=0.13, \
      TILevel4=0.09, \
      Filename=filename, \
      Stride=1, \
      Laser1AcqPower=95, \
      Laser2AcqPower=100 \
   )

def runCustomTrace( \
        acquisition_time, \
        exposure=0.01,
        dye_ids='20091214_A555, 20091214_A568, 20091214_A647, 20091214_Cy5p5', \
        label='', \
        chip_layout=default_chip_layout, \
        gridder_mode='REFERENCE_MCD', \
        zmw_roi=c10K_zmw_roi \
    ):
    '''Run a capture and extract traces'''
    print 'Running Trace Extraction'
    now = datetime.datetime.now()
    filename = now.strftime("%Y-%m%d-%H%M_Trace_") + label
    RunProtocol( \
        'hotStartSanity.py', \
        NeedTiFrames=True, \
        NeedLaserIllum=True, \
        NeedTraceExtraction=True, \
        UseMaxFrameSize=False, \
        AcquisitionTime=TimeSpan(0, 0, acquisition_time), \
        ExposureTime=exposure, \
        Filename=filename, \
        RunType='SEQUENCING', \
        DyeIds=dye_ids, \
        GridderMode=gridder_mode, \
        ChipLayout=chip_layout, \
        ZmwRoiType=zmw_roi_type_to_string(zmw_roi), \
        ZmwRoiOriginX=zmw_roi.center.x, \
        ZmwRoiOriginY=zmw_roi.center.y, \
        ZmwRoiExtentX=zmw_roi.extent.x, \
        ZmwRoiExtentY=zmw_roi.extent.y, \
        TILevel1=0.2, \
        TILevel2=0.095, \
        TILevel3=0.13, \
        TILevel4=0.09, \
        Laser1AcqPower=95, \
        Laser2AcqPower=100 \
    )

def runCustomTraceNoScan( \
        acquisition_time, \
        exposure=0.01,
        dye_ids='20091214_A555, 20091214_A568, 20091214_A647, 20091214_Cy5p5', \
        label='', \
        chip_layout=default_chip_layout, \
        gridder_mode='REFERENCE_MCD', \
        zmw_roi=c10K_zmw_roi \
    ):
    '''Run a capture and extract traces'''
    print 'Running Trace Extraction'
    now = datetime.datetime.now()
    filename = now.strftime("%Y-%m%d-%H%M_Trace_") + label
    RunProtocolNoScan( \
        'hotStartSanity.py', \
        NeedTiFrames=True, \
        NeedLaserIllum=True, \
        NeedTraceExtraction=True, \
        UseMaxFrameSize=False, \
        AcquisitionTime=TimeSpan(0, 0, acquisition_time), \
        ExposureTime=exposure, \
        Filename=filename, \
        RunType='SEQUENCING', \
        DyeIds=dye_ids, \
        GridderMode=gridder_mode, \
        ChipLayout=chip_layout, \
		ZmwRoiType=zmw_roi_type_to_string(zmw_roi), \
        ZmwRoiOriginX=zmw_roi.center.x, \
        ZmwRoiOriginY=zmw_roi.center.y, \
        ZmwRoiExtentX=zmw_roi.extent.x, \
        ZmwRoiExtentY=zmw_roi.extent.y, \
        TILevel1=0.2, \
        TILevel2=0.095, \
        TILevel3=0.13, \
        TILevel4=0.09, \
        Laser1AcqPower=95, \
        Laser2AcqPower=100 \
    )
 
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
        'hotStartSanity.py', \
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
        TILevel1=0.2, \
        TILevel2=0.091, \
        TILevel3=0.13, \
        TILevel4=0.09, \
        Laser1AcqPower=95, \
        Laser2AcqPower=100 \
    )

def getbsbr(fname):
  camb=instrument.BSBR.Camera
  ImageLogger.Instance.LogRaw(camb.Snapshot(True), fname+"all")
  time.sleep(2)
  instrument.BSBR.Illuminator.Enabled=False
  shutter1.BeginOpen(True)
  shutter2.BeginOpen(False)
  time.sleep(2)
  ImageLogger.Instance.LogRaw(camb.Snapshot(True), fname+"green")
  instrument.BSBR.Illuminator.Enabled=False
  shutter1.BeginOpen(False)
  shutter2.BeginOpen(True)
  time.sleep(2)
  ImageLogger.Instance.LogRaw(camb.Snapshot(True), fname+"red")
  instrument.BSBR.Illuminator.Enabled=True
  shutter1.BeginOpen(False)
  shutter2.BeginOpen(False)
  time.sleep(2)
  ImageLogger.Instance.LogRaw(camb.Snapshot(True), fname+"IR")
  instrument.BSBR.Illuminator.Enabled=True
  shutter1.BeginOpen(True)
  shutter2.BeginOpen(True)

def runProtoDarkCal75fps():
    """Capture dark calibration movie"""
    print 'Dark Calibration Capture'
    now = datetime.datetime.now()
    RunProtocolNoScan( \
        'hotStartSanity.py', \
        NeedTiFrames=False, \
        NeedLaserIllum=False, \
        NeedTraceExtraction=False, \
        UseMaxFrameSize=True, \
        AcquisitionTime=TimeSpan(0, 0, 20), \
        ExposureTime=0.01333, \
        Stride=20, \
        Filename=now.strftime("%Y%m%dT%H%M%S_darkcal_75fps"), \
        RunType='CAMERACALIBRATION_DARKFRAME' \
    )