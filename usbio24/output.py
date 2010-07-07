#!/usr/bin/env python

class RelayModule():
	"""Interface for relay board connected to USB I/O 24"""

	io = None
	port = None

	def __init__(self,io,port):
		self.io = io
		self.port = port.upper()

		# put all pins on the I/O board's port in output mode
		self.io.set_pin_direction(self.port,[])

	def set_state(self,activated_relays=[]):
		"""
		Activate the given relays and turn off the rest. It is important to
		note that we are really passing the state of each relay packed into
		one byte of data. So, turning on one relay in one call to this command
		followed by turning on another relay in a separate call will turn off
		the previous relay. Using RelayModule.activate will avoid this issue.
		"""

		relay_int = 0
		for relay in activated_relays:
			relay_int += 2 ** (relay - 1)

		self.io.write_port(self.port, relay_int)

	def reset(self):
		"""Convenience function to deactivate all relays"""
		self.set_state()

	def activate(self,relays=[]):
		"""
		Version 3 firmware allows for individual pins to be turned on/off, we do this
		via IOModule.set_pin_high.
		"""

		for relay in relays:
			self.io.set_pin_high(self.port, relay)

	def deactivate(self,relays=[]):
		"""
		Version 3 firmware allows for individual pins to be turned on/off, we do this
		via IOModule.set_pin_low.
		"""

		for relay in relays:
			self.io.set_pin_low(self.port, relay)

