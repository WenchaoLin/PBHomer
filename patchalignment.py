#
# Example patch, to use import from /vital/patches/<instname>.py
# This is a quick python port of my C# test class PatchAlignment.cs
#

import clr

from PacBio.Common.Services import *
from PacBio.Instrument.Interfaces.Alignment import *

class PatchAlignment(IStateMachineHook):
	"""Patch the aligner to remove and replace the chip if levelling fails"""

	def __init__(self, robot):
		self.robot = robot
		self.didTry = False # We only retry once

	@staticmethod
	def Install(inst):
		"""Construct and install our patch"""
		aligner = inst.ChipAlignmentAPI
		aligner.AddHook(PatchAlignment(inst.Robot))

	def Apply(self, stateMachine, typ, oldState, newState):
		"""See IStateMachineHook for documentation - in our case we look for failure of the levelling state"""

		if typ == HookType.PreTransition:
			if Prepare == newState:
				self.didTry = False	# Starting a new chip, so reset failure bit

			# FIXME, we should probably have the aligner enter a special abort rather than idle, but I
			# wanted to make this work as-is.
			if not self.didTry and LevelChip == oldState and Idle == newState:
				# Basic demo code - for real code be more careful about gripper usage - patches will never be easy to write
				self.robot.PickupChipFromStage(Gripper1)
				self.robot.MoveChipToStage(Gripper.Gripper1, True)
				self.didTry = True

				# Try again to enter level chip
				return LevelChip

PatchAlignment.Install(instrument)
