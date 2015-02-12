# Front end for executing protocol files from the homer shell.

import clr

from System.Collections import *
from System.IO import Path
from System.Reflection import Assembly
from System.Drawing import Rectangle
from System import Exception as System_Exception

clr.AddReference("System.Xml")
from System.Xml import *
from System import TimeSpan, DateTime

from PacBio.Instrument.Data.Seeding import *
from PacBio.Common.Data.Decl import *
from PacBio.Common.Diagnostics import *
from PacBio.Common.Prefs import *
from PacBio.Common.Utils import *
from PacBio.Common.IO import *
from PacBio.Instrument.Homer import *
from PacBio.Instrument.Protocols import *
from PacBio.Instrument.Interfaces import *
from PacBio.Instrument.Interfaces.Homer import *
from PacBio.Instrument.Interfaces.Movement import *
from PacBio.Instrument.Interfaces.RunControl import *
from PacBio.Instrument.Interfaces.Loader import *
from PacBio.Common.Data.DAF import *
from PacBio.Common.Scheduler import * 
from PacBio.Instrument.Analysis import *
from PacBio.Instrument.Analysis.Pipeline import *
import PacBio.Instrument.Analysis.Metadata
from PacBio.Common.Version import VersionUtils
from HomerApp import Program

import sys
import time
import datetime
import os

from robotics import *
 
import xml.dom.minidom
from xml.dom.minidom import parse, parseString
 
pds = str(Path.DirectorySeparatorChar)
exedir = Path.GetDirectoryName(Assembly.GetEntryAssembly().Location)
protocolsDir = Program.ProtocolsDir

logger = DiagManager.LogManager.LocalLogger(__name__ + ".py")

def UpdateMovieChipAcquisitionTables(md, mcs, plateName):
    # Update chip acquisition.
    from PacBio.Common.Data.OR import ChipAcquisition
    chipAcq = ChipAcquisition()
    from PacBio.Common.Data.DAF.API import *
    df = DAOFactory.CreateInstance[APIDAOFactory]()
    prefDAO = df.GetPreferenceDAO()
    cds = InstrumentContext.Instrument.CentralDataSvc
    path_pref = prefDAO.GetPreferenceByName("Display.Primary_Analysis", "Output_URI")
    output_uri = cds.GetDataItem("Display.Primary_Analysis", "Output_URI", DeclDataClassification.Prefs, Type.GetType(path_pref.ValueType)).ToString()
    output = Uri(output_uri)
    import clr
    clr.AddReference("System.Web")
    from System.Web import HttpUtility
    chipAcq.ResultDataFilePath = output.AbsoluteUri + "/" + HttpUtility.UrlPathEncode(plateName) + "/" + md.Sample.WellName + "_" + str(md.CollectionNumber)

    from PacBio.Common.Data.DAF import *
    try:
        transaction = DAFUtil.BeginTransaction()
        DAFUtil.GetSession().SaveOrUpdate(chipAcq)
        transaction.Commit()
    finally:
        DAFUtil.CommitTransaction()
        DAFUtil.CloseSession()

    # Update movie.
    from PacBio.Common.Data.OR import Movie
    from PacBio.Instrument.Interfaces import MovieContext
    mc = MovieContext.Parse(mcs)
    movie = Movie()
    movie.Look = 1                      # Assume that we have one look movies.
    movie.Description = mc.ToString()
    movie.ChipAcquisition = chipAcq

    try:
        transaction = DAFUtil.BeginTransaction()
        DAFUtil.GetSession().SaveOrUpdate(movie)
        transaction.Commit()
    finally:
        DAFUtil.CommitTransaction()
        DAFUtil.CloseSession()

    # Update primary analysis job to point to correct movie.
    from PacBio.Common.Jobs import *
    from NHibernate.Criterion import *
    jm = JobManager.Instance
    jobs = jm.GetJobs(Restrictions.Eq("JobType","PacBio.Instrument.Jobs.PrimaryAnalysisJob"),Restrictions.Eq("Description", mcs))
    if len(jobs) != 1:
        print "ERROR: found more than one associated primary job"
    
    job = jobs[0]
    job.ReferenceObjectUri = DataAccessUtils.BuildRefObjUri(movie, InstrumentContext.InstrumentName).ToString()
    try:
        transaction = DAFUtil.BeginTransaction()
        DAFUtil.GetSession().SaveOrUpdate(job)
        transaction.Commit()
    finally:
        DAFUtil.CommitTransaction()
        DAFUtil.CloseSession()

def CreateMetadata(pd = None, limsvol = None, volno = None, plateName = None):
    inst = InstrumentContext.Instrument
    now = datetime.datetime.now()
    now_dt = DateTime.Now
    one_yr_from_now = now_dt.AddYears(1)
    md = PacBio.Instrument.Analysis.Metadata.Metadata()
    md.InstCtrlVer = VersionUtils.SoftwareVersion
    md.SigProcVer = inst.OttoSvcVersion 
    md.Run = PacBio.Instrument.Analysis.Metadata.Run()
    md.Run.RunId = now.strftime('%y%m%d_%H%M%S_') + inst.Name
    md.Run.Name = md.Run.RunId
    md.Run.WhenCreated = now_dt
    md.Run.WhenStarted = now_dt
    md.Run.StartedBy = 'labtech'
    md.Movie = PacBio.Instrument.Analysis.Metadata.Movie()
    md.Movie.WhenStarted = now_dt
    md.Movie.DurationInSec = pd['AcquisitionTime'].TotalSeconds if pd else 60
    md.Movie.Number = 0
    md.Sample = PacBio.Instrument.Analysis.Metadata.Sample()
    md.Sample.Name = md.Run.Name
    md.Sample.PlateId = md.Sample.Name
    md.Sample.WellName = pd['SampleWellName'] if pd else 'A01'
    md.Sample.Concentration = 0
    md.Sample.SampleReuseEnabled = False 
    md.Sample.UseCount = 1
    md.Sample.Comments = 'No comment'
    md.Sample.DNAControlComplex = 'none'
    md.InstrumentId = '1234'
    md.InstrumentName = inst.Name
    md.CollectionProtocol = 'SanityCollectionProtocol'
    md.CollectionNumber = 1
    md.CellIndex = 0
    md.SetNumber = 1
    md.EightPac = PacBio.Instrument.Analysis.Metadata.SupplyKit()
    md.EightPac.Barcode = CreateManualBarcode('ChipStripAurum')
    md.EightPac.LotNumber = md.EightPac.Barcode[19:25]
    md.EightPac.PartNumber = md.EightPac.Barcode[15:19]
    md.EightPac.ExpirationDate = one_yr_from_now
    md.TemplatePrep = PacBio.Instrument.Analysis.Metadata.SupplyKitTemplate()
    md.TemplatePrep.Name = 'DNA Template Prep Kit 2.0 (250bp - 3Kb)'
    md.TemplatePrep.Barcode = '000001001540835123114'
    md.TemplatePrep.LotNumber = md.TemplatePrep.Barcode[:6]
    md.TemplatePrep.PartNumber = md.TemplatePrep.Barcode[7:16]
    md.TemplatePrep.ExpirationDate = one_yr_from_now
    md.TemplatePrep.AdapterSequence = tuple(['ATCTCTCTCttttcctcctcctc', 'cgttgttgttgttGAGAGAGAT'])
    md.TemplatePrep.InsertSize = 10000
    md.BindingKit = PacBio.Instrument.Analysis.Metadata.SupplyKitBinding()
    md.BindingKit.Name ='DNA/Polymerase Binding Kit XL 1.0'
    md.BindingKit.Barcode = '000001100150800123114'
    md.BindingKit.PartNumber = md.BindingKit.Barcode[:6]
    md.BindingKit.LotNumber = md.BindingKit.Barcode[7:16]
    md.BindingKit.ExpirationDate = one_yr_from_now
    md.SequencingKit = PacBio.Instrument.Analysis.Metadata.SupplyKitSequencing()
    md.SequencingKit.Name = 'ReagentPlate0'
    md.SequencingKit.Barcode = CreateManualBarcode('DWP_ReagentPlate8_C2_Std')
    md.SequencingKit.PartNumber = md.SequencingKit.Barcode[:6]
    md.SequencingKit.LotNumber = md.SequencingKit.Barcode[10:19]
    md.SequencingKit.ExpirationDate = one_yr_from_now
    md.SequencingKit.Protocol = 'C2ReagentMixingProtocol_DWP'
    md.ReagentTube0 = PacBio.Instrument.Analysis.Metadata.SupplyKitSequencing()
    md.ReagentTube0.Name = 'ReagentTube0-0'
    md.ReagentTube0.Barcode = CreateManualBarcode('ShallowTube')
    md.ReagentTube0.PartNumber = md.ReagentTube0.Barcode[:6]
    md.ReagentTube0.LotNumber = md.ReagentTube0.Barcode[10:19]
    md.ReagentTube0.ExpirationDate = one_yr_from_now
    md.ReagentTube1 = PacBio.Instrument.Analysis.Metadata.SupplyKitSequencing()
    md.ReagentTube1.Name = 'ReagentTube0-1'
    md.ReagentTube1.Barcode = CreateManualBarcode('OilTube')
    md.ReagentTube1.PartNumber = md.ReagentTube1.Barcode[:6]
    md.ReagentTube1.LotNumber = md.ReagentTube1.Barcode[10:19]
    md.ReagentTube1.ExpirationDate = one_yr_from_now
    md.Primary = PacBio.Instrument.Analysis.Metadata.Primary()
    md.Primary.Protocol = 'BasecallerV1'
    md.Primary.ConfigFileName = '1-3-0_Standard_C2.xml'
    md.Primary.ResultsFolder = 'Analysis_Results'
    if volno and plateName:
        md.Primary.CollectionPathUri = 'rsy://oixfr:rfxio@mp-f030-io/' + volno + '/RS_DATA_STAGING/' + inst.Name + '/' + plateName + '/' + md.Sample.WellName + '_1'
    md.Primary.CollectionFileCopy = tuple([PacBio.Instrument.Analysis.Metadata.PapOutputFile.Pulse, PacBio.Instrument.Analysis.Metadata.PapOutputFile.Fasta, PacBio.Instrument.Analysis.Metadata.PapOutputFile.Fastq])
    md.Secondary = PacBio.Instrument.Analysis.Metadata.Secondary()
    md.Secondary.ProtocolName = ''
    md.Secondary.ProtocolParameters = ''
    md.Secondary.CellCountInJob = 0
    if limsvol:
        kv1 = PacBio.Instrument.Analysis.Metadata.KeyValue()
        kv1.key = 'svc:/CentralDataSvc/#Display.Sample_Metadata.User_Defined_Field_1'
        kv1.Value = 'LIMS_IMPORT=' + limsvol
        md.Custom = tuple([kv1])
    return md


reagentmixing = "FCRReagentMixingProtocol_DWP.py"
acquisition = "FCRAcquisitionProtocol.py"

# Fold most of the stuff from the "driver" scripts into one function.
def RunProtocol(proto, scan=True, **options):
    """Run a named protocol file, optionally overriding protocol parameters"""
    i = InstrumentContext.Instrument
    executor = i.ProtocolExecutor
    #uncomment the following two lines if you are running on simulator and don't want to wait
    #ProtocolLiquidToolKit.RealPauses = False
    #ScheduleRunner.AllowEarlyStarts = True   
    #ScheduleRunner.RunSingleThreaded = True
    
    loadResult = executor.LoadProtocolFile(proto)
    logger.Info("protocol load result:" + str(loadResult.LoadedProtocolIdentifier))
    if not loadResult.Success:
    	print "Protocol not loaded, error: " + str(loadResult)
    	return
    
    if scan:
        protType = executor.GetProtocolType()
        if protType == ProtocolType.ReagentMixingProtocol:
	        UseDefaultBarcodes()
        else:
            UseDefaultBarcodes(False)
        i.TemplateReagentDrawer.SnapshotSamplePlateState()
        if (not protType == ProtocolType.ReagentMixingProtocol) and (not protType == ProtocolType.AcquisitionProtocol):
            i.TemplateReagentDrawer.ClearManualBarcode(MVLocationName.SamplePlate)
        i.DrawerOracle.AddPointIfLocationMissing(MVLocationName.MixingPlate)
        InventoryScan()

    d = { }
    params = executor.GetProtocolParameters()

    # Pull in default params/values
    for pname in params.Keys:
        d[pname] = params[pname]

    # force us to a 1 min movie
    #d[ProtocolParameter.ACQUISITION_TIME].Value = "00:01:00"
    for k, v in options.iteritems():
        d[k].Value = v

    for k in sorted(d.keys()):
        logger.Info("Parameter: " + str(d[k]))

    # Warning: HACK! temporary workaround for lack of exception handling in ProtocolExecutor
    exeResult = ProtocolExecuteResult()
    exeResult.Success = False
    exeResult.FailureMessage = "(not started)"
    try:
        exeResult = executor.Execute(d)
    except System_Exception, e:
        print 'Exception running protocol:'
        print str(e)
    if exeResult.Success:
        logger.Info('Finished executing protocol successfully.')
    else:
        logger.Info('executing protocol result:' + exeResult.FailureMessage)
    return executor.ProtocolContext

def RunProtocolNoScan(proto, **options):
	return RunProtocol(proto, False, **options)

# FIXME - Probably needs to be done in the composition scripts in the future.
def InitProtocols():
    pass
	#pipetteIdealCalib(pp1, 'Aqueous', 1250, 125)
	#wm = WellZMap.Instance
	#wm.SetZOffset("*TestJigTube*", WellZPosition.AboveWellPosition, -0.05)
	#wm.SetZOffset("*TestJigTube*", WellZPosition.WellTopPosition, 0.0)
	#wm.SetZOffset("*TestJigTube*", WellZPosition.WellBottomPosition, 0.028)

# Run init once, right now.
InitProtocols()

# protocol utility functions
def RaiseRobot():
    InstrumentContext.Instrument.Robot.RControl.RaiseZ()
    
def DisposeTip(pipetter):
    InstrumentContext.Instrument.Robot.DisposePipetteTip(pipetter)
    
def DisposeChip(gripper):
    InstrumentContext.Instrument.Robot.DisposeChip(gripper)
    
def RemoveChipFromStage(gripper):
    InstrumentContext.Instrument.Robot.PickupChipFromStage(gripper)
    InstrumentContext.Instrument.Robot.DisposeChip(gripper)
    
def UpdateReagentKitType(key='8chipDWPkit_v0.9', typeFile='ReagentKit_8chipDWP.xml'):
    dms=InstrumentContext.Instrument.DataSeedingManagerSvc
    xmlfile = exedir + pds + "ReagentKitType" + pds + typeFile
    dms.UpdateReagentKitType(key, xmlfile)
    
def InventoryScan():
    i = InstrumentContext.Instrument
    executor = i.ProtocolExecutor
    scanResult = executor.InventoryScan()
    logger.Info("inventory scan result:" + str(scanResult.FailureMessage))
    
def OpenCloseDrawers():
    i = InstrumentContext.Instrument
    chipTipDrawer = i.ChipsTipsDrawer
    chipTipDrawer.Open()
    chipTipDrawer.Close()
	
    tempDrawer = i.TemplateReagentDrawer
    tempDrawer.Open()
    tempDrawer.Close()
    
def ImportSS(ssFile='Protocols//mySS.csv'):
    i=InstrumentContext.Instrument
    sss=i.SampleSheetSvc

    start=time.clock()
    sss.SampleSheetImport(ssFile)
    end=time.clock()

    logger.Info("ImportSS time elapsed = " + str(end-start) + " seconds")
    
def ExportSS(outputFile, SamplePlateBarcode):
    i=InstrumentContext.Instrument
    sss=i.SampleSheetSvc

    start=time.clock()
    sss.SampleSheetExport(outputFile, SamplePlateBarcode)
    end=time.clock()

    logger.Info("ExportSS time elapsed = " + str(end-start) + " seconds")
 
def DeleteSS(barcode):
    i=InstrumentContext.Instrument
    sss=i.SampleSheetSvc

    start=time.clock()
    sss.DeletePlate(barcode)
    end=time.clock()

    logger.Info("DeleteSS time elapsed = " + str(end-start) + " seconds")
    
def ValidateSS(ssFile='Protocols//mySS.csv'):
    i=InstrumentContext.Instrument
    sss=i.SampleSheetSvc

    start=time.clock()
    sss.SampleSheetValidate(ssFile)
    end=time.clock()

    logger.Info("ValidateSS time elapsed = " + str(end-start) + " seconds")
    
def UpdateSS(ssFile='Protocols//mySS.csv'):
    i=InstrumentContext.Instrument
    sss=i.SampleSheetSvc

    start=time.clock()
    sss.SampleSheetUpdate(ssFile)
    end=time.clock()

    logger.Info("UpdateSS time elapsed = " + str(end-start) + " seconds")
    
def ValidatePlateDefinition(plateFile):
    i=InstrumentContext.Instrument
    validator=i.RunValidator
    sreader = StreamReader(FileStream(plateFile, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
    inputString = sreader.ReadToEnd()
    
    outString = validator.ValidateSamplePlateDefinition(inputString)
    
    xmlDoc = XmlDocument()
    xmlDoc.Load(StringReader(outString))
    
    print
    xmlDoc.Save(Console.Out)
    print
    
def DeleteInventoryData():
    i = InstrumentContext.Instrument
    i.TemplateReagentDrawer.ClearManualBarcode(None)
    i.TemplateReagentDrawer.UnLoadAllTrays()
    i.ChipsTipsDrawer.ClearManualBarcode(None)
    i.ChipsTipsDrawer.UnLoadAllTrays()
    instLoading = i.InstrumentLoading
    instLoading.ClearUploadedPlateDefinition()
    executor = i.ProtocolExecutor
    executor.DeleteInventoryData()
    executor.DeleteRunData()
       
def DeleteSeedingData():
    i = InstrumentContext.Instrument
    SMgr = i.DataSeedingManagerSvc
    SMgr.DeleteAllSeedingData()


# runType = 'Standard' or 'Strobe' or 'FCRFinal'
# useTestJig = True will now give real barcodes to the chip strips so that the ChipLayout can be passed. Change by PH on 3/9/11
def RunSamplePlate(samplePlate='ABC01234', runType='C2_Std', useTestJig=False, createBarcodes=True):
    """Starts running a full acqusition and analysis protocols"""
    
    inst = InstrumentContext.Instrument
    
    if useTestJig: # real chips only supported for LPR (War) and FCR (Laurel) layouts
        enableSWATJig()
        if (createBarcodes == True): # only supporting FCR barcodes with TestJig
            UseManualTestJigBarcode(True, '00','111111', 'FCR', '000001', '123113')

    # simulated defaults as well as the equivalent of opening and closing the drawer
    # make sure to run InventoryScan() after these steps to commit the inventory state
    if (createBarcodes == True):
       UseDefaultBarcodes(True, samplePlate, runType)

    inst.TemplateReagentDrawer.TemplatePlate.PresenceState = PlatePresenceState.Unknown
    inst.TemplateReagentDrawer.SnapshotSamplePlateState()
    inst.TemplateReagentDrawer.SetManualBarcode(MVLocationName.SamplePlate, samplePlate)
    inst.DrawerOracle.AddPointIfLocationMissing(MVLocationName.MixingPlate)
    
    runner = inst.RunController
    #uncomment the following three lines if you are running on simulator and don't want to wait
    #runner.RunAcquisitionsInParallel = False
    #ProtocolLiquidToolKit.RealPauses = False
    #ScheduleRunner.AllowEarlyStarts = True
    
    scanResult = runner.InventoryScan()
    logger.Info("inventory scan result: " + str(scanResult.FailureMessage))
    
    if (inst.TemplateReagentDrawer.UserResolution.State == UserResolutionState.BarcodeMismatchAndHasPlateDefinition):
        inst.TemplateReagentDrawer.AcceptPlate()
        inst.TemplateReagentDrawer.UploadPlateDefinition(samplePlate)
        logger.Info("after accepting plate, user resolution state: "+str(inst.TemplateReagentDrawer.UserResolution.State))
    if (inst.TemplateReagentDrawer.UserResolution.State != UserResolutionState.NoResolutionNeeded):
        if not inst.TemplateReagentDrawer.UploadPlateDefinition(samplePlate):
            logger.Error("No plate definition? Check sample sheet import. User resolution state: "+str(inst.TemplateReagentDrawer.UserResolution.State))
            return
    #reagent tube check
    if ((inst.TemplateReagentDrawer.TemplateReagentTray.ReagentKitPlate0.PresenceState == PlatePresenceState.Present) and 
    (inst.TemplateReagentDrawer.TemplateReagentTray.ReagentTube0_0.PresenceState != PlatePresenceState.Present and
         inst.TemplateReagentDrawer.TemplateReagentTray.ReagentTube0_1.PresenceState != PlatePresenceState.Present)):          
             logger.Error("Reagent Tube is missing")
             return
         
    if ((inst.TemplateReagentDrawer.TemplateReagentTray.ReagentKitPlate1.PresenceState == PlatePresenceState.Present) and 
    (inst.TemplateReagentDrawer.TemplateReagentTray.ReagentTube1_0.PresenceState != PlatePresenceState.Present and
         inst.TemplateReagentDrawer.TemplateReagentTray.ReagentTube1_1.PresenceState != PlatePresenceState.Present)):          
             logger.Error("Reagent Tube is missing")
             return
        
    
    #at this step, the manual barcodes should be absorbed by inventory scan
    #delete manual barcode to eliminate any side effects
    #per bug 13175, this isn't needed
    #ClearManualBarcodes()
    
    time.sleep(5)
    handle = runner.BeginExecuteRun()
    return handle

def WaitForRun(handle):
    """Wait for the current run to complete"""
    runner = InstrumentContext.Instrument.RunController
    exeResult = runner.EndExecuteRun(handle)
    logger.Info('run result:' + str(exeResult.FailureMessage))
    return exeResult

def GenSampleSheet(nChips=1, protocol="Standard Seq v3", readLength=1, addParams="", SSName="ABC01234", insertSize=2000, filename='genericSS.csv',comments='',outputPath='//usmp-data',LIMS='myfield2',sampleName='Sm_ABC01234',CELLINDEX='myfield3'):
	""" Generate a sample sheet for an arbitrary number of chips. Return file path. """
	fname = '/home/pbi/%s'%filename
	fhandle = open(fname, 'w')
	print >> fhandle, "Sample Sheet File Format for Pacific Biosciences Springfield Instrument,,,,,,,,,,,,,,,,,,,"
	print >> fhandle, ""
	print >> fhandle, "Version,1.0.0,,,,,,,,,,,,,,,,,,"
	print >> fhandle, ""
	print >> fhandle, "Unique ID,"+SSName+",,,,,,,,,,,,,,,,,,"
	print >> fhandle, "Type,Plate,,,,,,,,,,,,,,,,,,"
	print >> fhandle, "Owner,John Smith,,,,,,,,,,,,,,,,,,"
	print >> fhandle, "Created By,jfsmith,,,,,,,,,,,,,,,,,,"
	print >> fhandle, "Comments,"+comments+",,,,,,,,,,,,,,,,,,"
	print >> fhandle, "Output Path,pbids:"+outputPath+",,,,,,,,,,,,,,,,,,"
	print >> fhandle, ""
	print >> fhandle, "Well No.,Sample Name,DNA Template Prep Kit Box Barcode,Prep Kit Parameters,Binding Kit Box Barcode,Binding Kit Parameters,Collection Protocol,CP Parameters,Basecaller,Basecaller Parameters,Secondary Analysis Protocol,Secondary Analysis Parameters,Sample Comments,User Field 1,User Field 2,User Field 3,User Field 4,User Field 5,User Field 6,Results Data Output Path"
	wellNames = ["A01","B01","C01","D01","E01","F01"]
	for i in range(0, nChips):
		if protocol=="DefaultRDProtocol":
			templatePrepBarcode = "004012444444444091513"
			bindingKitBarcode = "004012555555555091513"
		elif protocol=="Standard Seq v3":
			templatePrepBarcode = "004012001540726091513"
			bindingKitBarcode = "004012001672551091513"
		elif protocol=="Standard Seq Fast Chem v2":
			templatePrepBarcode = "004012001540726091513"
			bindingKitBarcode = "004012001672551091513"
		else:
			templatePrepBarcode = "004012001540726091513"
			bindingKitBarcode = "004012001672551091513"
		print >> fhandle, wellNames[i/8]+","+sampleName+","+templatePrepBarcode+",,"+bindingKitBarcode+",UsedControl=true," + protocol + ",AcquisitionTime=" + str(readLength) + "|NumberOfCollections=1|InsertSize="+str(insertSize)+addParams+",Default,,,,"+sampleName+",myfield1,"+LIMS+","+CELLINDEX+",myfield4,myfield5,myfield6,"
	
	fhandle.close()
	return fname

def RunOneChipSanity(allowEarlyStarts=True,IsMixReagents=False,IsMoveChips=True,reseedDB=True,generateJobName=False):
    """Do all the stuff needed to run acquisition and analysis protocols on a single test chip for sanity"""
    #delete inventory data from DB, also clears drawer inventory state
    if reseedDB:
        DeleteInventoryData()
        DeleteSeedingData()
        SeedDB()

    if generateJobName:
        now = datetime.datetime.now()
        jobname = now.strftime('%Y%m%dT%H%M%S_SanityTest') 
        fh = open(protocolsDir + pds + 'oneWellSSSanity.csv')
        ssfile = open('/tmp/oneWellSSSanity_AutoGenJobName.csv', 'w')
        for line in fh:
          newline = line.replace('SanityTest', jobname)
          ssfile.write(newline) 
        fh.close()
        ssfile.close()
        ImportSS('/tmp/oneWellSSSanity_AutoGenJobName.csv')
    else:
        #import a new defintion of sample sheet
        ImportSS(protocolsDir + pds + 'oneWellSSSanity.csv')

    # allow early starts
    if allowEarlyStarts:
        ScheduleRunner.AllowEarlyStarts = True
        ProtocolLiquidToolKit.RealPauses = False

    ProtocolTask.IsMixReagents = IsMixReagents
    ProtocolTask.IsMoveChips = IsMoveChips
    
    #run the plate job
    return RunSamplePlate()

def RunOneChip():
    """Do all the stuff needed to run acqusition and analysis protocols on a single test chip"""
    #delete inventory data from DB, also clears drawer inventory state
    DeleteInventoryData()
    
    #import a new defintion of sample sheet
    ImportSS(protocolsDir + pds + 'oneWellSS.csv')
    
    #run the plate job
    return RunSamplePlate(runType='FCRFinal')
    #return WaitForRun(RunSamplePlate())

def RunChipsRD(nChips, movieLength=15, addParams="", SSName="ABC01234", delInv=False):
  if delInv:
    DeleteInventoryData()
  ImportSS(GenSampleSheet(nChips, "DefaultRDProtocol", movieLength, addParams, SSName))
  RunSamplePlate(samplePlate=SSName, runType="RD")

def RunChipsFCR(nChips, readLength=15, addParams="",  SSName="ABC01234", delInv=False):
    """Do all the stuff needed to run acqusition and analysis protocols on any number of test chips"""
    #delete inventory data from DB, also clears drawer inventory state
    if delInv:
        DeleteInventoryData()
    
    #import a new defintion of sample sheet
    ImportSS(GenSampleSheet(nChips, "Standard Seq v1", readLength, addParams, SSName))
    
    #run the plate job
    return RunSamplePlate(samplePlate=SSName, runType='FCRFinal')
    #return WaitForRun(RunSamplePlate())

def RunOneChipNoClearInventory():
    """Do all the stuff needed to run acqusition and analysis protocols on a single test chip"""
    #import a new defintion of sample sheet
    ImportSS(exedir + pds + 'Protocols' + pds + 'oneWellSS.csv')
    
    #run the plate job
    return RunSamplePlate()
    #return WaitForRun(RunSamplePlate())

def RunLimsChip():
    """Do all the stuff needed to run acqusition and analysis protocols on a single test chip"""
    #delete inventory data from DB, also clears drawer inventory state
    DeleteInventoryData()
    
    #import a new defintion of sample sheet
    ImportSS(protocolsDir + pds + 'testLimsSS.csv')
    
    #run the plate job
    return RunSamplePlate('Lims01234')
    #return WaitForRun(RunSamplePlate())
        
def RunThreeChip():
    """Do all the stuff needed to run acqusition and analysis protocols on 3 chips"""
    #delete inventory data from DB, also clears drawer inventory state
    DeleteInventoryData()
    
    #import a new defintion of sample sheet
    ImportSS(protocolsDir + pds + 'threeWellSS.csv')
    
    #run the plate job
    return WaitForRun(RunSamplePlate())
    
    
def SeedDB(seedingFilePath = None):
    i = InstrumentContext.Instrument
    SMgr = i.DataSeedingManagerSvc
    # Done automatically now
	# SMgr.InstrumentNodeName = AppSettings.Instance["NodeName"];
    start=time.clock()
    SMgr.SeedDBFromFile(seedingFilePath)
    end=time.clock()
    
    i.DataCompatibilitySvc.QueryAndInitializeCompatibityMatrixData()
    i.BarcodeDecodingSvc.QueryAndInitializePPN()
    i.RunValidator.QueryDataFromDB()
    
    logger.Info("SeedDB time elapsed = " + str(end-start) + " seconds")
    
def UpdateSeedingData():
    i = InstrumentContext.Instrument
    SMgr = i.DataSeedingManagerSvc
    start=time.clock()
    SMgr.UpdateSeedingData()
    end=time.clock()
    
    logger.Info("UpdateSeedingData time elapsed = " + str(end-start) + " seconds")
    
def PeekAtTipBox(boxNum):
    i = InstrumentContext.Instrument
    tipBox = i.ChipsTipsDrawer.PipetteTipTray.GetTipBox(boxNum)
    #format printout statements
    print ' ',     
    for i in range(1,10):
	   print i, '  ',
    for i in range(10,25):
	   print i, ' ',
 	  
    r = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']    
    for i in range(0, 16):
       print
       print r[i],
       for j in range(0, 24):
          if tipBox.Present[i, j]:
             print 'T ',' ',
          else:
	         print 'F ',' ',
       
    print    
    
def CreateNewReagentBlock(proto):
    i = InstrumentContext.Instrument
    executor = i.ProtocolExecutor
    
    OpenCloseDrawers()
    InventoryScan()

    loadResult = executor.LoadProtocolFile(proto)
    logger.Info("protocol load result:" + str(loadResult.LoadedProtocolIdentifier))
    
    executor.ProtocolContext.Parameters = executor.GetProtocolParameters()
    executor.Protocol.DefineTasks(executor.ProtocolContext.Parameters)
    
    time.sleep(10)
    executor.ProtocolContext.CreateNewReagentBlock()

def SetSamplePlateBarcode(barcode):
    inst = InstrumentContext.Instrument
    inst.TemplateReagentDrawer.SetManualBarcode(MVLocationName.SamplePlate, barcode)

def SetReagentPlateBarcode(barcode):
    # reagent plate 0 barcode only
    inst = InstrumentContext.Instrument
    inst.TemplateReagentDrawer.SetManualBarcode(MVLocationName.ReagentPlate0, barcode)
    
def ClearManualBarcodes():
    # clear out all manual barcodes
    inst = InstrumentContext.Instrument
    drawer = inst.TemplateReagentDrawer
    chips = inst.ChipsTipsDrawer
    
    # we clear out manual barcodes defined in UseDefaultBarcodes function
    drawer.ClearManualBarcode(None)    
    chips.ClearManualBarcode(None)

	# runType is Standard or Strobe
def UseDefaultBarcodes(createNew=True, samplePlateBarcode='ABC01234', runType='C2_Std'):
    inst = InstrumentContext.Instrument
    drawer = inst.TemplateReagentDrawer
    chips = inst.ChipsTipsDrawer
    
    drawer.SetManualBarcode(MVLocationName.SamplePlate, samplePlateBarcode)
    
    if createNew:
        if runType == 'Strobe':
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-0", CreateManualBarcode('ChipStrip'))
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-1", CreateManualBarcode('ChipStrip'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate0, CreateManualBarcode('DWPReagentPlate8Strobe'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate1, CreateManualBarcode('DWPReagentPlate8Strobe'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            
        elif runType == 'Standard':
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-0", CreateManualBarcode('ChipStrip'))
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-1", CreateManualBarcode('ChipStrip'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate0, CreateManualBarcode('DWPReagentPlate8'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate1, CreateManualBarcode('DWPReagentPlate8'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            
        elif runType == 'FCRStandard':
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-0", CreateManualBarcode('ChipStripFCR'))
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-1", CreateManualBarcode('ChipStripFCR'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate0, CreateManualBarcode('DWPReagentPlate8FCR'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate1, CreateManualBarcode('DWPReagentPlate8FCR'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))

        elif runType == 'FCRFinal':
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-0", CreateManualBarcode('ChipStripFCR'))
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-1", CreateManualBarcode('ChipStripFCR'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate0, CreateManualBarcode('DWPReagentPlate8FCRFinal'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate1, CreateManualBarcode('DWPReagentPlate8FCRFinal'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))

        elif runType == 'FCRStrobe':
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-0", CreateManualBarcode('ChipStripFCR'))
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-1", CreateManualBarcode('ChipStripFCR'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate0, CreateManualBarcode('DWPReagentPlate8FCRStrobe'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate1, CreateManualBarcode('DWPReagentPlate8FCRStrobe'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))

        elif runType == 'C2_Std':
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-0", CreateManualBarcode('ChipStripAurum'))
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-1", CreateManualBarcode('ChipStripAurum'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate0, CreateManualBarcode('DWP_ReagentPlate8_C2_Std'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "1", CreateManualBarcode('OilTube'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate1, CreateManualBarcode('DWP_ReagentPlate8_C2_Std'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "1", CreateManualBarcode('OilTube'))
            
        elif runType == 'C2_24':
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-0", CreateManualBarcode('ChipStripAurum'))
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-1", CreateManualBarcode('ChipStripAurum'))
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-2", CreateManualBarcode('ChipStripAurum'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate0, CreateManualBarcode('DWP_ReagentPlate24_C2_Std'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube24'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "1", CreateManualBarcode('OilTube24'))
                        
        elif runType == 'C2_Fast':
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-0", CreateManualBarcode('ChipStripAurum'))
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-1", CreateManualBarcode('ChipStripAurum'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate0, CreateManualBarcode('DWP_ReagentPlate8_C2_Fast'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "1", CreateManualBarcode('OilTube'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate1, CreateManualBarcode('DWP_ReagentPlate8_C2_Fast'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "1", CreateManualBarcode('OilTube'))
            
        elif runType == 'RD':
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-0", CreateManualBarcode('ChipStripAurum'))
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-1", CreateManualBarcode('ChipStripAurum'))
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-2", CreateManualBarcode('ChipStripAurum'))
            chips.SetManualBarcode(MVLocationName.ChipStrip + "-3", CreateManualBarcode('ChipStripAurum'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate0, CreateManualBarcode('RDReagentPlate'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "1", CreateManualBarcode('OilTube'))
            
            drawer.SetManualBarcode(MVLocationName.ReagentPlate1, CreateManualBarcode('RDReagentPlate'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "0", CreateManualBarcode('ShallowTube'))
            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "1", CreateManualBarcode('OilTube'))

        else:
            print "We don't recognise the run type"
            return    
    else:
        # let's use the existing *latest* reagent barcodes in DB - this is necessary if you RunProtocol(acquisition)
        try:
            DAFUtil.GetSession()
            DAFUtil.BeginTransaction()
            
            query = "select barcode from reagentkit where name = 'ReagentPlate0' order by whenmodified desc limit 1"
            result = DAFUtil.GetSession().CreateSQLQuery(query).UniqueResult();
            if result is not None:
	            drawer.SetManualBarcode(MVLocationName.ReagentPlate0, result)
 
            query = "select barcode from reagentkit where name = 'ReagentTube0-0' order by whenmodified desc limit 1"
            result = DAFUtil.GetSession().CreateSQLQuery(query).UniqueResult();
            if result is not None:
	            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "0", result)
            
            query = "select barcode from reagentkit where name = 'ReagentTube0-1' order by whenmodified desc limit 1"
            result = DAFUtil.GetSession().CreateSQLQuery(query).UniqueResult();
            if result is not None:
	            drawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "1", result)

            query = "select barcode from reagentkit where name = 'ReagentPlate1' order by whenmodified desc limit 1"
            result = DAFUtil.GetSession().CreateSQLQuery(query).UniqueResult();
            if result is not None:
	            drawer.SetManualBarcode(MVLocationName.ReagentPlate1, result)
 
            query = "select barcode from reagentkit where name = 'ReagentTube1-0' order by whenmodified desc limit 1"
            result = DAFUtil.GetSession().CreateSQLQuery(query).UniqueResult();
            if result is not None:
	            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "0", result)
            
            query = "select barcode from reagentkit where name = 'ReagentTube1-1' order by whenmodified desc limit 1"
            result = DAFUtil.GetSession().CreateSQLQuery(query).UniqueResult();
            if result is not None:
	            drawer.SetManualBarcode(MVLocationName.ReagentTube1 + str(MVLocationName.Separator) + "1", result)
            
            DAFUtil.CommitTransaction()
            DAFUtil.CloseSession()
        except System_Exception, e:
            print 'Exception create reagent manual barcode:'
            print str(e)  
            DAFUtil.CommitTransaction()
            DAFUtil.CloseSession()     
            
def UpdateSAWebAddress(saUri='http://usmp-hdp003/smrtportal/api'):
    inst = InstrumentContext.Instrument
    cds = inst.CentralDataSvc
    
    cds.StoreDataItem("Display.Secondary_Analysis", "Web_Server_Address", DeclDataClassification.Prefs, "The secondary analysis web server address", saUri)


def UseManualTestJigBarcode(realChips=False,umOffset='00',presentInfo='111111',objectName='FCR',lotnum='000001',expdate='123113'):
    inst = InstrumentContext.Instrument
    chips = inst.ChipsTipsDrawer
    if realChips:
        chips.SetManualBarcode(MVLocationName.TestJig, CreateTestJigBarcode(umOffset,presentInfo,objectName,lotnum,expdate))
    else:
        chips.SetManualBarcode(MVLocationName.TestJig, "unknown")

#Present info: top left to bottom right, whether a chip is there or not
#e.g.: x x o (where x indicates no chip and o indicates a chip)
#      o o x  would correspond to 001110
#If a failure occurs, returns the barcode 'FailedToCreate' (which will fail validation on length constraints)
def CreateTestJigBarcode(umOffset='00',presentInfo='111111',objectName='FCR',lotnum='000001',expdate='123113'):
   if objectName == 'LPR':
       ppn = '0001'
   elif objectName == 'FCR':
       ppn = '0003'
   elif objectName == 'TSMC':
       ppn = '0015'
   elif objectName == 'Aurum':
       ppn = '0018'
   else:
       print "Can't get ppn from object name given. Need LPR, FCR, TSMC, or Aurum."
       return 'FailedToCreate'
   if not len(presentInfo)==6:
       print "Need presentInfo (second argument) to be of length six (that's how many slots for chips that a SWATJig has)."
       return 'FailedToCreate'
   try:
       chips = (int(presentInfo[5]),int(presentInfo[4]),int(presentInfo[3]),int(presentInfo[2]),int(presentInfo[1]),int(presentInfo[0]))
   except:
       print 'Invalid presence information. Not creating a barcode.'
   presentThree = 0 #start with the last two (ignored for now) not present
   for j in range(2,8):
       presentThree += 2**(7-j)*chips[j-2]
   try:
       DAFUtil.GetSession()
       DAFUtil.BeginTransaction()
       
       query = "select barcode from chipstrip where barcode like :partName"
       
       resultList = DAFUtil.GetSession().CreateSQLQuery(query).SetString("partName", "%"+ppn+"%").List();
       
       DAFUtil.CommitTransaction()
       DAFUtil.CloseSession()
       
       # add createdBarcodes for this ppn to the resultList
       if ppn in createdBarcodes:
           bc = createdBarcodes[ppn]
           resultList.AddRange(createdBarcodes[ppn])
       
       if resultList.Count == 0:
           barcode = "0" + "0000001" + str(presentThree).zfill(3) + umOffset + "00" + ppn + lotnum + expdate + "8"
       else:
           _ppn_ = []
           for b in resultList:
               _ppn_.insert(0, b[1:8])
           
	       # sort the list from small to large     
	       _ppn_.sort()
           
           # increment by 1 from lot number + serial number
           new_sn = int(_ppn_[len(_ppn_)-1]) + 1
           barcode = "0" + str(new_sn).zfill(7) + str(presentThree).zfill(3) + umOffset + "00" + ppn + lotnum + expdate + "8"
       
       # add the new barcode to the global list
       if ppn in createdBarcodes:
	       bclist = createdBarcodes[ppn]
	       bclist.append(barcode)
	       createdBarcodes[ppn] = bclist
       else:
           createdBarcodes[ppn] = [ barcode ]
       
       print objectName + " TestJig: " + barcode
       return barcode
       
   except System_Exception, e:
       print 'Exception create test jig manual barcode:'
       print str(e)  
       DAFUtil.CommitTransaction()
       DAFUtil.CloseSession() 
       return 'FailedToCreate'

createdBarcodes = {}  
def CreateManualBarcode(objectName):
   NewBarcode = DataAccessUtils.CreateManualBarcodes(objectName)
   if (not String.IsNullOrEmpty(NewBarcode)):
      return NewBarcode
   else:
      #Put new part numbers and naming conventions here if immediately needed
      #Otherwise update the DataAccessUtils utility instead.
      ppn = ''
      #The following object names are given here as an example to how one would add part numbers
      if objectName == 'MyNewReagentPlate':
         ppn = '999999999'
      elif objectName == 'ChipStripNewAndImproved':
         ppn = '0090'
      else:
         print "objectName must be one of these: DWP_ReagentPlate24_C2_Std, DWPReagentPlateFull, DWP_ReagentPlate8_C2_Std, DWP_ReagentPlate8_C2_Fast, RDReagentPlate, DWPReagentPlate8FCRFinal, DWPReagentPlate8FCRStrobe, DWPReagentPlate8FCR, DWPReagentPlate8Strobe, DWPReagentPlate8, DWPReagentPlate24, ShallowTube, ShallowTube24, DeepTube, ChipStrip, ChipStripFCR, ChipStripAurum"
         return
   try:
        DAFUtil.GetSession()
        DAFUtil.BeginTransaction()
        
        query = ''
        if objectName.Contains('ChipStrip'):
            query = "select barcode from chipstrip where barcode like :partName"
        else:
            query = "select barcode from reagentkit where barcode like :partName"
        
        resultList = DAFUtil.GetSession().CreateSQLQuery(query).SetString("partName", "%"+ppn+"%").List();
        
        DAFUtil.CommitTransaction()
        DAFUtil.CloseSession()
        
        # add createdBarcodes for this ppn to the resultList
        if ppn in createdBarcodes:
            bc = createdBarcodes[ppn]
            resultList.AddRange(createdBarcodes[ppn])
        
        if resultList.Count == 0:
            if not objectName.Contains('ChipStrip'):
                barcode = "000001001" + ppn + "123113"
            else:
                shortbarcode = "0" + "0000001" + "255" + "00" + "00" + ppn + "000001" + "123113"
                checkdigit = DataAccessUtils.CalculateCheckDigit(shortbarcode)
                barcode = shortbarcode+str(checkdigit)
        else:
            _ppn_ = []
            for b in resultList:
                if not objectName.Contains('ChipStrip'):
                    _ppn_.insert(0, b[0:9])
                else:
                    _ppn_.insert(0, b[1:8])
                        
	        # sort the list from small to large     
	        _ppn_.sort()
            
            # increment by 1 from lot number + serial number
            new_sn = int(_ppn_[len(_ppn_)-1]) + 1
            if not objectName.Contains('ChipStrip'):
                barcode = str(new_sn).zfill(9) + ppn + "123113"
            else:
                shortbarcode = "0" + str(new_sn).zfill(7) + "255" + "00" + "00" + ppn + "000001" + "123113"
                checkdigit = DataAccessUtils.CalculateCheckDigit(shortbarcode)
                barcode = shortbarcode+str(checkdigit)
                            
        # add the new barcode to the global list
        if ppn in createdBarcodes:
	        bclist = createdBarcodes[ppn]
	        bclist.append(barcode)
	        createdBarcodes[ppn] = bclist
        else:
            createdBarcodes[ppn] = [ barcode ]
            
        print objectName + ": " + barcode
        return barcode
            
   except System_Exception, e:
        print 'Exception create reagent manual barcode:'
        print str(e)
   finally:
        DAFUtil.CommitTransaction()
        DAFUtil.CloseSession() 

def SaveKeepTraceFilePreference(yesno):
    '''
    The difference between this function the one below it is that this one persists the setting in the database
    in order for future versions (and reboots) to have the option enabled/disabled
    '''
    logger.Info("SaveKeepTraceFilePreference(" + str(yesno) + ") has been called.")
    inst = InstrumentContext.Instrument
    cds = inst.CentralDataSvc
    cds.StoreDataItem('Display.Primary_Analysis', 'Keep_Trace_Files', DeclDataClassification.Prefs, DatumScope.Release, 'Transfer trace files?', yesno)
    cds.EditDeclRepository.UpdateRepository(DeclDataClassification.Prefs)
    
def SaveKeepPulseFilePreference(yesno):
    '''
    The difference between this function the one below it is that this one persists the setting in the database
    in order for future versions (and reboots) to have the option enabled/disabled
    '''
    logger.Info("SaveKeepPulseFilePreference(" + str(yesno) + ") has been called.")
    inst = InstrumentContext.Instrument
    cds = inst.CentralDataSvc
    cds.StoreDataItem('Display.Primary_Analysis', 'Keep_Pulse_Files', DeclDataClassification.Prefs, DatumScope.Release, 'Transfer pulse files?', yesno)
    cds.EditDeclRepository.UpdateRepository(DeclDataClassification.Prefs)
    
def KeepTraceFiles(yesno):
    inst = InstrumentContext.Instrument
    cds = inst.CentralDataSvc
    
    cds.StoreDataItem("Display.Primary_Analysis", "Keep_Trace_Files", DeclDataClassification.Prefs, "Whether to keep trace files", yesno)
    
def KeepPulseFiles(yesno):
    inst = InstrumentContext.Instrument
    cds = inst.CentralDataSvc
    
    cds.StoreDataItem("Display.Primary_Analysis", "Keep_Pulse_Files", DeclDataClassification.Prefs, "Whether to keep pulse files", yesno)
    
def ProduceFASTAFiles(yesno):
    inst = InstrumentContext.Instrument
    cds = inst.CentralDataSvc
    
    cds.StoreDataItem("Display.Primary_Analysis", "Produce_FASTA_Files", DeclDataClassification.Prefs, "Whether to produce FASTA files", yesno)
    
def ProduceFASTQFiles(yesno):
    inst = InstrumentContext.Instrument
    cds = inst.CentralDataSvc
    
    cds.StoreDataItem("Display.Primary_Analysis", "Produce_FASTQ_Files", DeclDataClassification.Prefs, "Whether to produce FASTQ files", yesno)

    
def TraceSampler(mdFile):
    '''
    Runs an analysis of pseudo-random subset of the trace file associated with
    the given metadata file (if it exists) and copies the results off the 
    instrument.  The files are modified with a suffix to distinguish them from
    full dataset results.
    '''
    pc = PipelineController.Instance
    absPath = LocateMdFile(mdFile)
    
    if absPath is None:
        return
          
    pc.SubmitProtocolJob(absPath, "LprSampler")

def LocateMdFile(mdFile):
    '''
    Locates the pap01 path which holds the given metadata file.
    mdFile - The metadata file associated with the acquisition (filename only)
    
    returns the path on pap01 to the file or None if not found.
    '''
    
    found = False
    print "Locating metadata file on pipeline blades ...\n"
    for i in 2,3,4:
    
        mdUri = Uri("file:///mnt/imports/pap0%d/spool/%s" % (i,mdFile))
        
        absPath = UriTools.UriToFilepath(mdUri)
        if os.path.exists(absPath):
            print "Found path on pap0%d\n" % (i)
            found = True
            break
        
    if found != True:
        print "Could not locate metadata file %s" % (mdFile)
        return None
 
    return absPath

def ShowPlateDefinition(plateID):
    try:
        DAFUtil.GetSession()
        DAFUtil.BeginTransaction()
        
        query = 'select pv.validationresult from platevalidation pv, plate p where p.platevalidationid = pv.platevalidationid and p.barcode = :pid'
        resultList = DAFUtil.GetSession().CreateSQLQuery(query).SetString("pid", plateID).List();
        
        if resultList.Count == 0:
            print "There is no associated PlateValidation data for this plate"
            return
        else:
            xmlDoc = XmlDocument()
            xmlDoc.Load(StringReader(resultList[0]))
            print
            xmlDoc.Save(Console.Out)
            print
        
        DAFUtil.CommitTransaction()
        DAFUtil.CloseSession()
        
    except System_Exception, e:
        print 'Exception showPlateDefinition'
        print str(e)  
        DAFUtil.CommitTransaction()
        DAFUtil.CloseSession()  
        
def ShowLoadedInventory():
    loaded = InstrumentContext.Instrument.RunController.CurrentLoadedInventory
    loadedKit = loaded.LoadedReagentKit
    for kit in loadedKit:
        print "Reagent Kit Name: " + kit.Name
        print "Reagent Kit PPN: " + kit.PartNumber
        print "Reagent Kit AvailableReagentsInChips: " + str(kit.AvailableReagentsInChips)
        for tube in kit.LoadedReagentTube:
            print "---Reagent Tube Name: " + tube.Name
            print "---Reagent Tube PPN: " + tube.PartNumber
            print "---Reagent Tube AvailableReagentsInChips: " + str(tube.AvailableReagentsInChips)
        print
    
    loadedChips = loaded.LoadedChipLayout
    for chipLayout in loadedChips:
        print
        print "Loaded ChipLayout: " + chipLayout.PartNumber
    
    print
    print "loaded # of chips: " + str(loaded.NumberOfPresentCells)
    
    print
    print "Loaded left tips: " + str(loaded.PresentTips.Left) 
    print "Loaded Right tips: " + str(loaded.PresentTips.Right)  
 
## Add function to run sample plate without robot
def RunManualSample(samplePlate='ABC01234', chipStripBarcode='Unknown',enzymeBarcode='Unknown',reagentPlateBarcode='Unknown',oilTubeBarcode='Unknown'):
   ProtocolTask.IsMoveChips = True
   ProtocolTask.IsMixReagents = False
   ScheduleRunner.AllowEarlyStarts = True
   ProtocolLiquidToolKit.RealPauses = False
   try:
      enableSWATJig()
      print '='*80
      print 'R U N N I N G   M A N U A L   S A M P L E'.center(80,' ')
      print '-'*80
      ProtocolTask.SkipPostCleanupJob = True
      i.TemplateReagentDrawer.SetManualBarcode(MVLocationName.ReagentPlate0,reagentPlateBarcode)
      i.TemplateReagentDrawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "0", enzymeBarcode)
      i.TemplateReagentDrawer.SetManualBarcode(MVLocationName.ReagentTube0 + str(MVLocationName.Separator) + "1", oilTubeBarcode)
      i.ChipsTipsDrawer.SetManualBarcode(MVLocationName.TestJig,chipStripBarcode)
      i.ChipsTipsDrawer.SetManualBarcode("ChipStrip-0", CreateManualBarcode('ChipStripAurum')) #Need this to trick inventory to have chips
      print "Reagent plate: " + reagentPlateBarcode
      print "OS enzyme: " + enzymeBarcode
      print "Oil: " + oilTubeBarcode
      print "TestJig: " + chipStripBarcode
      result = WaitForRun(RunSamplePlate(samplePlate, 'C2_Std', True, False))
      ProtocolTask.SkipPostCleanupJob = False
      print ' Done '.center(80,'-')
      if result.FailureMessage:
         print result.FailureMessage
   finally:
     ClearManualSample()

def ClearManualSample():
   ProtocolTask.IsMoveChips = True
   ProtocolTask.IsMixReagents = True
   ScheduleRunner.AllowEarlyStarts = False
   ProtocolLiquidToolKit.RealPauses = True
   ClearManualBarcodes()
   disableSWATJig()

def GenManualSOPSS(interact=True, ssFileName='Default', uniqueID=None, StageStart = 'False', acqTime=1, destination='TestJig',
                   layout='3.x', setNum='Both', limsDest='2310474',
                   sampleName='ManualSample', comment='Default comment',
                   chipStripBarcode='Unknown', cellIndex='Unknown', enzymeTubeBarcode='Unknown', reagentPlateBarcode='Unknown',
                   oilTubeBarcode='Unknown'):
    """

    \t interact           [bool]   : True or False. Default value is True. True starts an interactive session.
    \t ssFileName         [string] : Name of the sample sheet without path or extentions. Default value is 'Default'.
    \t uniqueID           [string] : Unique id for the acquisition. Default value is None.
    \t StageStart         [string] : Perform spike at the stage. Default value is 'False'. Only enabled on select instruments.   
    \t acqTime            [integer]: Acquisition time in minutes. Should be greater than 0. Default value is 1.
    \t destination        [string] : The destination of the chip after acqisition. Possible values are
                                     'TestJig', 'WasteBin', 'Stage'. Default value is 'Stage'.
    \t setNum             [string] : The number of looks. Possible values are 'One' or 'Both'. Default value is 'Both'.
                                     If the layout is '2.x' then value 'Both' is incompatible.
    \t limsDest           [string] : The LIMS destination folder. This requires rsync and the volume to be mapped for
                                     the users destination experiment. Default is for pbids://rsync-manual/RS_DATA_STAGING/Manual.
                                     User SHOULD MAKE SURE THIS IS VALID. Default is vol52 and 2310474.  
    \t sampleName         [string] : The name of the sample could be passed to the sample sheet. Default value is
                                     Manual_Sample
    \t comment            [string] : The comment could be passed to the sample sheet. Default value is
                                     Default comment
    \t chipStripBarcode   [string] : This is the barcode of the chip strip from where the chip was extracted. The
                                     value could be entered or scaned in using a barcode reader. 
                                     Default value is 'Unknown'.
    \t cellIndex          [integer]: This the location from where the chip was extracted from the strip. Valid values
                                     are from 0 to 8. 0 is translated to 'Unknown' and placed in the sample
                                     sheet. Other values from 1 to 8 are passed as is to the sample sheet. The default
                                     value is 'Unknown'.
    \t enzymeTubeBarcode  [string] : This is the barcode of the OS enzyme tube. The value could be entered
                                     or scaned in using a barcode reader. The default value is 'Unknown'.
    \t reagentPlateBarcode [string]: This is the barcode of the reagent kit plate. The value could be entered
                                     or scaned in using a barcode reader. The default value is 'Unknown'.
    \t oilTubeBarcode     [string] : This is the barcode of the oil tube. The value could be entered
                                     or scaned in using a barcode reader. The default value is 'Unknown'.
    """
    from PacBio.Common.Services import URIResolver, URIConstants
    from PacBio.Common.Version.VersionUtils import SoftwareVersion
    
    stdDefaults = {'csvfilename':'ManualSOP_SS', 'StageStart':'False', 'acqtime':1, 'destination':1, 'setnum':2, 'limsdest':'2310474',
            'samplename':'ManualSample','chipstripbarcode':'Unknown','cellindex':[0],'enzymetubebarcode':'Unknown','reagentplatebarcode':'Unknown','oiltubebarcode':'Unknown'}
    currDefaults = None
    destStr   = ('','TestJig','WasteBin','Stage')
    setStr    = ('', 'One', 'Both')
    limsDefault = '2310474'
    unknownDefault = 'Unknown'
    [pink, blue, green, yellow, red] = range(5)
    banerWidth = 100

    def __colorText(userString, color):
        textColor = ['\033[95m', '\033[94m', '\033[92m', '\033[93m', '\033[91m']
        ENDC = '\033[0m'        
        return '%s%s%s'%(textColor[color], userString, ENDC)

    def __yellowPrint(message):
        print __colorText(message, yellow)

    def __readNumber(itype, prompt, defaultValue = None):
        retNumber = None
        retNumberStr = None
        if defaultValue != None:
            nPrompt = '%s [%s]: '%(prompt,__colorText(defaultValue,pink))
        else:
            nPrompt = '%s: '%prompt
        while retNumber == None:
            try:
                retNumberStr = raw_input(nPrompt)
                uInput = retNumberStr.strip()
                if uInput == '' and defaultValue != None:
                    uInput = '%s'%defaultValue
                retNumber = itype(uInput)
            except:
                if sys.exc_info()[0].__name__ == 'KeyboardInterrupt':
                    __yellowPrint('User aborted the session!')
                    raise
                print __colorText('%s: %s [%s]'%(sys.exc_info()[0].__name__, sys.exc_info()[1], retNumberStr.strip()), red)
        return retNumber
    
    def __readString(prompt, defaultValue = None):
        retStr = None
        retString = None
        if str.IsNullOrEmpty(defaultValue):
            nPrompt = '%s: '%prompt
        else:
            nPrompt = '%s [%s]: '%(prompt,__colorText(defaultValue,pink))
        while str.IsNullOrEmpty(retStr):
           try:
              retString = raw_input(nPrompt)
              uInput = retString.strip().replace(',',' ')
              if uInput == '' and defaultValue:
                  retStr = defaultValue
              else:
                  retStr = uInput
           except:
                if sys.exc_info()[0].__name__ == 'KeyboardInterrupt':
                    __yellowPrint('User aborted the session!')
                    raise
                print __colorText('%s: %s [%s]'%(sys.exc_info()[0].__name__, sys.exc_info()[1], retStr), red)
        return retStr
    
    def __confirm(prompt):
        ans = ''
        while ans not in ['y','Y','n','N']:
            try:
                ans = raw_input('%s %s '%(prompt, __colorText('(Y,N)',yellow))).strip()
            except:
                if sys.exc_info()[0].__name__ == 'KeyboardInterrupt':
                    __yellowPrint('User aborted the session!')
                    raise
                print __colorText('%s: %s [%s]'%(sys.exc_info()[0].__name__, sys.exc_info()[1], retNumberStr.strip()), red)
        return ans in ['Y','y']

    def __getDestination(defaultValue = 3):
        dNum = 0
        while dNum not in [1,2,3]:
            dNum = __readNumber(int,'Please choose the destination of chip after the run 1) TestJig, 2) Waste Bin, 3) Stage', defaultValue)
        return destStr[dNum], dNum

    def __getSetNum(defaultValue = 2):
        dNum = 0
        while dNum not in [1,2]:
            dNum = __readNumber(int,'Please choose the set 1) One, 2) Both', defaultValue)
        return setStr[dNum], dNum

    def __assignDefault(value, defaultValue):
        if str.IsNullOrEmpty(value):
            return defaultValue.replace(',',' ')
        return value.replace(',',' ')

    def __getPreviousDefaults():
        if not os.path.exists('/home/pbi/manualsopsrc/default.txt'):
            return {}
        try:
            dFile = open('/home/pbi/manualsopsrc/default.txt', 'r')
            line = ''
            for l in dFile:
                line += l
            d = eval(line)
            if type(d) == type({}):
                return d
            else:
                print line
                __yellowPrint('Type [%s] was not expected!'%type(d))
        except:
            print __colorText('%s: %s'%(sys.exc_info()[0].__name__, sys.exc_info()[1]), red)
            return {}
        return {}

    def __saveDefaults(d):
        try:
            if not os.path.exists('/home/pbi/manualsopsrc'):
                os.mkdir('/home/pbi/manualsopsrc')
            dFile = open('/home/pbi/manualsopsrc/default.txt', 'w')
            dFile.write('%s'%d)
            dFile.close()
        except:
            print __colorText('%s: %s'%(sys.exc_info()[0].__name__, sys.exc_info()[1]), red)

    if interact:# Interactive mode starts here
        bannerText = '%s\n%s\n%s'%('='*banerWidth,
                     'I N T E R A C T I V E   S A M P L E   S H E E T   C R E A T I O N'.center(banerWidth,' '),
                     '-'*banerWidth)
        print __colorText(bannerText, green)

        __yellowPrint('\nPlease avoid special characters and non-printable characters in the input.')
        __yellowPrint('Values in the square bracket are the default values and pressing <enter> will assign them.\n')
        currDefaults = stdDefaults
        if os.path.exists('/home/pbi/manualsopsrc/default.txt'):
            if __confirm('Would you want to use the previous run\'s values as defaults?'):
                currDefaults = __getPreviousDefaults()
                if currDefaults == {}:
                    __yellowPrint('Could not get the defaults from the previous run! Using standard defaults.')
                    currDefaults = stdDefaults
                elif len(stdDefaults) != len(currDefaults):
                    for k in stdDefaults.keys():
                        if not currDefaults.has_key(k):
                            currDefaults[k] = stdDefaults[k]
                else:
                    print 'Successfully loaded previously used values as defaults'

        # Flag to set for StageHS. Only for enabled instruments!
        if __confirm('Do you want perform Stage Hot Start?'):
            useStageStart = 'True'
        else:
            useStageStart = 'False'
        currDefaults['StageStart'] = useStageStart
        print 'Use Stage Start        : %s'%__colorText(useStageStart, pink)

        ssFileName = __readString('Please enter the sample sheet name', currDefaults['csvfilename'])
        currDefaults['csvfilename'] = ssFileName        
        ssFileName = '%s%s.csv'%(ssFileName, time.strftime('_%y%m%d_%H%M'))
        print 'Sample Sheet Name        : %s'%__colorText(ssFileName, pink)
        uniqueID = __readString('Please enter the unique id', currDefaults['csvfilename'])
        uniqueID = '%s%s'%(uniqueID, time.strftime('_%y%m%d_%H%M'))
        print 'Unique Id Used           : %s'%__colorText(uniqueID, pink)
 
        acqTime = 0
        while acqTime < 1:
            acqTime = __readNumber(int, 'Please enter acquisition time in minutes<integer>',currDefaults['acqtime'])
            if acqTime < 1: __yellowPrint('Acquisition time should be an integer greater than 0')
        print 'Acquisition time duration: %s Min.'%__colorText(acqTime, pink)
        currDefaults['acqtime'] = acqTime
 
        # Only allow destination choice for non-stage HS case.
        if useStageStart == 'False':
            destination, selectedItem = __getDestination(currDefaults['destination'])
            print 'Chip destination         : %s'%__colorText(destination, pink)
            currDefaults['destination'] = selectedItem
    
        setNum, selectedItem = __getSetNum(currDefaults['setnum'])
        print 'Set number               : %s'%__colorText(setNum, pink)
        currDefaults['setnum'] = selectedItem
        limsDest = __readString('Please enter the LIMS folder', currDefaults['limsdest'])
        print 'LIMS folder              : %s'%__colorText(limsDest, pink)
        currDefaults['limsdest'] = limsDest
        sampleName = __readString('Please enter the sample name comment', currDefaults['samplename'])
        print 'Sample name              : %s'%__colorText(sampleName, pink)
        currDefaults['samplename'] = sampleName

        chipStripBarcode = __readString('Please scan or enter the chip strip barcode',currDefaults['chipstripbarcode'])
        if (chipStripBarcode==unknownDefault):
            print 'Using default chip strip barcode'
            chipStripBarcode = CreateManualBarcode('ChipStripAurum')
            cellIndexNumber = 'Unknown'
            print 'Cell location: '+str(cellIndexNumber)
            currDefaults['chipstripbarcode'] = unknownDefault
            currDefaults['cellindex'] = [0]
        else:    
            print 'Chip strip barcode       : %s'%__colorText(chipStripBarcode, pink)
            # Track which cellIndex has been used for THIS INSTANCE of the strip barcode. Not globally tracking used barcodes in DB.
            cellIndex = -1   
            while (cellIndex < 1) or (cellIndex > 8) or (cellIndex in currDefaults['cellindex']):
                cellIndex = __readNumber(int, 'Please enter the location from where the chip was extracted %s'%__colorText('(1..8)', yellow),currDefaults['cellindex'][len(currDefaults['cellindex'])-1])
                cellIndexNumber = cellIndex
                if (cellIndex < 1) or (cellIndex > 8):
                    __yellowPrint('Value [%s] is out of range (1..8)'%cellIndex)
                    __yellowPrint('Must specify strip position for real barcode')
                if (cellIndex in currDefaults['cellindex']) & (cellIndex != 0):
                    __yellowPrint('Value [%s] has already been used for this strip'%cellIndex)
            print 'Cell location            : %s'%__colorText(cellIndex, pink)
            currDefaults['cellindex'].append(cellIndex)
            currDefaults['chipstripbarcode'] = chipStripBarcode

        enzymeTubeBarcode = __readString('Please scan or enter the OS enzyme tube barcode',currDefaults['enzymetubebarcode'])
        print 'OS enzyme tube barcode   : %s'%__colorText(enzymeTubeBarcode, pink)
        currDefaults['enzymetubebarcode'] = enzymeTubeBarcode
        reagentPlateBarcode = __readString('Please scan or enter the reagent plate barcode',currDefaults['reagentplatebarcode'])
        print 'Reagent plate barcode   : %s'%__colorText(reagentPlateBarcode, pink)
        currDefaults['reagentplatebarcode'] = reagentPlateBarcode
        oilTubeBarcode = __readString('Please scan or enter the oil tube barcode',currDefaults['oiltubebarcode'])
        print 'Oil tube barcode   : %s'%__colorText(oilTubeBarcode, pink)
        currDefaults['oiltubebarcode'] = oilTubeBarcode
        print __colorText(' Done '.center(banerWidth,'-'), green)
        __saveDefaults(currDefaults)
        print
    # Original interactive mode ends here
    else:
        ssFileName = time.strftime(ssFileName+'_%y%m%d_%H%M.csv')
        uniqueID = time.strftime('DefaultManualSOP_%y%m%d_%H%M') 
        __yellowPrint('** Using Default Options **')
        chipStripBarcode = CreateManualBarcode('ChipStripAurum')

    secondLook = setNum == 'Both'
    SScomment = '%s for Homer Version %s'%(time.strftime('New plate created on %A %B %d %Y - %H:%M:%S'),SoftwareVersion) 

    proto = 'Manual Seq'
    if useStageStart == 'False':
       GenSampleSheet(nChips=1,protocol=proto,readLength=acqTime,addParams='|ChipDestination='+destination+'|Use2ndLook='+str(secondLook)+'|StageHS=False',SSName=uniqueID,insertSize=10000,filename=ssFileName,comments=SScomment,outputPath='//rsync-manual/RS_DATA_STAGING/Manual',LIMS='LIMS_IMPORT='+str(limsDest),sampleName=sampleName,CELLINDEX='CELLINDEX18='+str(cellIndex))
    else:
       GenSampleSheet(nChips=1,protocol=proto,readLength=acqTime,addParams='|ChipDestination='+destination+'|Use2ndLook='+str(secondLook)+'|StageHS=True', SSName=uniqueID,insertSize=10000,filename=ssFileName,comments=SScomment,outputPath='//rsync-manual/RS_DATA_STAGING/Manual',LIMS='LIMS_IMPORT='+str(limsDest),sampleName=sampleName,CELLINDEX='CELLINDEX18='+str(cellIndex))
    
    # Set manual barcodes if real barcodes not provided
    if (enzymeTubeBarcode == unknownDefault): 
        enzymeTubeBarcode = CreateManualBarcode('ShallowTube')
    if (oilTubeBarcode == unknownDefault): 
        oilTubeBarcode = CreateManualBarcode('OilTube')
    if (reagentPlateBarcode == unknownDefault):
        reagentPlateBarcode = CreateManualBarcode('DWP_ReagentPlate8_C2_Std')
    
    # Coding the real cellIndex doesn't work yet
    if (cellIndex == unknownDefault):
        errCode = '255' # Unknown chip index always populates full strip of default barcode
    else: # Make sure cellIndex is always unique and odd so chip comes from TestJig-0
        if (cellIndexNumber % 2): errCode = '00'+str(cellIndexNumber)
        else: errCode = '0'+str(cellIndexNumber+9)   
    
    chipStripBarcode =  chipStripBarcode[0:8]+errCode+chipStripBarcode[11:32]

    print 'Sample Sheet [%s] is created successfully\n'%ssFileName
    print __colorText(' Command Sequence '.center(banerWidth,'='), green) 
    print "ImportSS('/home/pbi/%s')"%ssFileName
    print "RunManualSample('%s','%s','%s','%s','%s')"%(uniqueID,chipStripBarcode,enzymeTubeBarcode,reagentPlateBarcode,oilTubeBarcode)
