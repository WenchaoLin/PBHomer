from datetime import *
from homershell import *
from PacBio.Common.Scheduler import *

def EnsureDirExists(p):
    d = os.path.dirname(p)
    if not os.path.exists(d):
	    os.makedirs(d)
 

def ReseedDB():
    DeleteInventoryData()
    DeleteRunData()
    DeleteSeedingData()
    SeedDB()

def MySchedulerProgressChanged(sender, args):
    print "."
    
def MySchedulingBegins(sender, args):
    print "."

def MySchedulingEnds(sender, args):
    print "."

def MyTaskStartEvent(task, args):
    print ".............................................."
    print ".............................................."
    print "Task: " + task.DisplayName + " Start"
    print ".............................................."
    print ".............................................."

def MyTaskFinishEvent(task, args):
    print ".............................................."
    print ".............................................."
    print "Task: " + task.DisplayName + " Finish"
    print ".............................................."
    print ".............................................."

def MyStepStartEvent(step, steparg):
    print ".............................................."
    print ".............................................."
    print "Step: " + steparg.Task.DisplayName + " Start (%s -> %s)" % (step.Source, step.Target)
    print ".............................................."
    print ".............................................."

def MyStepFinishEvent(step, steparg):
    print ".............................................."
    print ".............................................."
    print "Step: " + steparg.Task.DisplayName + " Finish (%s -> %s)" % (step.Source, step.Target)
    print ".............................................."
    print ".............................................."

def MyProjectScheduled(sender, args):
    job = instrument.RunController.CurrentPlateJob
    project = job.ProtocolContext.ScheduledProject
    name = job.MappedJob.Description
    print ". Project Scheduled (%s)." % name
    for entry in project.Schedule.Entries:
        entry.Task.TaskStartEvent += MyTaskStartEvent
        entry.Task.TaskFinishEvent += MyTaskFinishEvent
        for step in entry.Task.StepList:
	        step.StepStartEvent += MyStepStartEvent
	        step.StepFinishEvent += MyStepFinishEvent
	    
	path = "rendered_schedules/";
    EnsureDirExists(path)
    cwd = os.getcwd()
    os.chdir(path)    
    project.RenderSchedule("%s-schedule.html" % (name))  
    os.chdir(cwd)

def MyRunStateChangedHandler(sender, args):
    state = instrument.RunController.CurrentRunState
    print ".............................................."
    print ".............................................."
    print "instrument.RunController.RunState: %s" % state
    print ".............................................."
    print ".............................................."
    
    if state == RunState.Running:
        job = instrument.RunController.CurrentPlateJob
        scheduler = instrument.RunController.CurrentPlateJob.Scheduler
        scheduler.SchedulingBegins += MySchedulingBegins
        scheduler.SchedulingEnds += MySchedulingEnds
        scheduler.ProgressChanged += MySchedulerProgressChanged
        job.ProjectScheduled += MyProjectScheduled	

instrument.FSM.SkipStabilization = True
instrument.RunController.IgnoreSystemErrors = True
instrument.RunController.RunStateChanged += MyRunStateChangedHandler
DeleteInventoryData()
allowEarlyStarts()

def VerboseScheduler():
    BacktrackScheduler.Verbose = True
    BacktrackScheduler.ExtremelyVerbose = True

def TestLongRun():
    DeleteInventoryData()
    allowEarlyStarts()
    ImportSS("bin/Debug/Protocols/oneWellFCR.csv")
    RunSamplePlate("ABC01234", runType='FCRFinal')

