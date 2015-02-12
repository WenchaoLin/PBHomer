import sys
import os

if os.name=='posix':
   sys.path.append(r'/home/schang/development/Integration/Springfield/FrameWork/sivlib')
   sys.path.append(r'/home/schang/development/Integration/Springfield/FrameWork/testdir/TestRobot')
   #sys.path.append(r'/home/schang/development/Integration/private/schang')
elif os.name=='nt':
   sys.path.append(r'C:\development\Integration\Springfield\FrameWork\sivlib')
   sys.path.append(r'C:\development\Integration\Springfield\FrameWork\testdir\TestRobot')

from robotics import *

