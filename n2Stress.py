from time import strftime

def n2Stress(p, cycles):
  '''
  Pipette N2 stress test
  p - Pipette.Pipette1 or Pipette.Pipette2
  cycles - number of engage/disengage cycles
  log file in /home/pbi/n2StressLog
  '''
  for i in range(cycles):
    f = open('/home/pbi/n2StressLog','a')
    r.EngageAccumulator(p)
    print strftime("%Y-%m-%d %H:%M:%S") + "\tengage " + str(i) + "\tL: " + str(z.CurrentPosition[2]) + "\tR: " + str(z.CurrentPosition[0])
    f.write(strftime("%Y-%m-%d %H:%M:%S") +"\tengage " + str(i) + "\tL: " + str(z.CurrentPosition[2]) + "\tR: " + str(z.CurrentPosition[0]) + "\n")
    time.sleep(5)
    r.DisengageAccumulator(p)
    print strftime("%Y-%m-%d %H:%M:%S") + "\tdisengage " + str(i) + "\tL: " + str(z.CurrentPosition[2]) + "\tR: " + str(z.CurrentPosition[0])
    f.write(strftime("%Y-%m-%d %H:%M:%S") + "\tdisengage " + str(i) + "\tL: " + str(z.CurrentPosition[2]) + "\tR: " + str(z.CurrentPosition[0]) + "\n")
    time.sleep(5)
    if p==Pipette.Pipette1:
      rc.MoveZ(-0.06, 0)
    elif p==Pipette.Pipette2:
      rc.MoveZ(-0.06, 2)
    f.close()
  rc.RaiseZ()