#RunOneChip()

allowEarlyStarts()
i.FSM.SkipStabilization=True
instrument.Acquisition.Params.ComponentControl='Pre;off;0:n;0:n|Post;off;0:n;0:n|Gridder;off;0:n;0:n'
pc = PipelineController.Instance