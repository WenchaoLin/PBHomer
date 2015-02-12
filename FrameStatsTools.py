clr.AddReference("PacBio.Instrument.Acquisition")
from PacBio.Instrument.Acquisition import CameraUtils

global fs_util
global fs_fileMover


fs_logger = DiagManager.LogManager.LocalLogger("FrameStatsTool")
fs_cs = instrument.CameraSet
fs_util = CameraUtils(fs_cs, fs_logger)
fs_fileMover = RsyncFileMover()


def frameStats(pap01WorkingDir, exposure, frameCount, stride=10, correctFrames=True) :
    global fs_util
    global fs_fileMover
    fs_llc = instrument.AcqCalibration.LowLevelCalibration
    # actually do the acquisition
    fs_ce = fs_util.DoFrameStats(exposure, frameCount, stride)
    # prepare to push to the frame stats store (FSS)
    fs_llc.FrameStatsStore.ClearFrameStats()
    # describde the acquisition (note, this is extensible)
    conditionData = Dictionary[str, str]()
    conditionData["Exposure"] = str(exposure)
    conditionData["FrameCount"] = str(frameCount)
    conditionData["Stride"] = str(stride)
    # move to and label in the FSS
    fs_llc.FrameStatsStore.PushFrameStats(conditionData)
    # apply dark correction to the frames
    if (correctFrames) :
        fs_llc.FrameStatsStore.CorrectFrames()
    # make a file name
    uniqueName = fs_llc.MakeUniqueName()
    fullPathNRTFss = fs_llc.GetFullPath(uniqueName, "IntermediateDataFile")
    # produce file
    fs_llc.FrameStatsStore.Write(fullPathNRTFss)
    # move back to homer
    fs_fileMover.CopyOneFile("nrt",fullPathNRTFss,"pap01",pap01WorkingDir,True,False)
