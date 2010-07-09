#!/usr/bin/env python

"""Interface with USB I/O 24 R"""

from serial import Serial
from struct import pack,unpack

class InvalidMode(Exception):
	pass

class InvalidPort(Exception):
	pass

class InvalidPin(Exception):
	pass

class InvalidData(Exception):
	pass

class IOModule():
	"""
	Communicates with a USB I/O 24 module and implements the command API of the standard firmware.
	"""

	device = ''
	driver = None

	def __init__(self,device='/dev/ttyUSB0',timeout=1):
		self.device = device
		self.driver = Serial(device,timeout=timeout)
		self.set_mode(1)

	def __str__(self):
		return 'IOModule @ ' + self.device

	def _validate_port(self,port):
		if port.upper() not in ['A','B','C']:
			raise InvalidPort

	def _validate_pin(self,pin):
		if pin < 1 or pin > 8:
			raise InvalidPin

	def _validate_data(self,data):
		if int(data) < 0 or int(data) > 255:
			raise InvalidData

	def set_mode(self,mode):
		"""
		Sets the operational mode of the I/O board. Mode 1 is the "simpler"
		of the two. According to the docs, mode 2 is different because:

			* All reads have a port designator (a,b, or c) before the data
			* All auto sends have a port designator before the data
			* All writes to the port that change the port will result in a port data auto send

		Currently, this module can not yet handle mode 2.
		"""

		if mode not in [1,2]:
			raise InvalidMode

		cmd = pack('B', mode)
		self.driver.write(cmd)
		
	def identify(self):
		"""
		Request's the device's "identity." Expect a newline-terminated response similar
		to "USB I/O 24"
		"""

		cmd = '?'
		self.driver.write(cmd)
		return self.driver.readline()

	def read_port(self,port):
		"""Reads one byte of data from the given port. Response is returned as an int"""

		self._validate_port(port)

		cmd = port.lower()
		self.driver.write(cmd)

		response = self.driver.read()
		return unpack('B', response)[0]

	def write_port(self,port,data):
		"""
		Writes one byte of data to the given port. Data should be an int <= 255 (one byte int)
		"""

		self._validate_port(port)
		self._validate_data(data)

		cmd = pack('cB', port.upper(), int(data))
		self.driver.write(cmd)

	def set_pin_high(self,port,pin):
		"""Sets specific pin high"""

		self._validate_port(port)
		self._validate_pin(pin)

		if port.upper() == 'A':	pin_int = 0
		if port.upper() == 'B':	pin_int = 8
		if port.upper() == 'C':	pin_int = 16
		pin_int += (pin - 1)

		cmd = pack('cB', 'H', pin_int)
		self.driver.write(cmd)

	def set_pin_low(self,port,pin):
		"""Sets specific pin low"""

		self._validate_port(port)
		self._validate_pin(pin)

		if port.upper() == 'A':	pin_int = 0
		if port.upper() == 'B':	pin_int = 8
		if port.upper() == 'C':	pin_int = 16
		pin_int += (pin - 1)

		cmd = pack('cB', 'L', pin_int)
		self.driver.write(cmd)

	def _set_pin_direction_raw(self,port,arg):
		"""
		Sends a "set pin direction" command. If a pin's bit is high,
		that sets the pin's direction as input.
		"""

		self._validate_port(port)
		cmd = pack('ccB', '!', port.upper(), arg)
		self.driver.write(cmd)

	def set_pin_direction(self,port,input_pins=[]):
		"""
		A convenience function for setting the pin's direction. The IO board's
		"set pin direction" command takes a 1-byte argument that consists of each
		pin's bit value if they are to be configured for input. The table of pins
		and their bit values are below, but we use the expression 2 ** (pin - 1)
		instead of doing a dictionary lookup.

		PIN 	Bit Value
		1	1
		2	2
		3	4
		4	8
		5	16
		6	32
		7	64
		8	128
		"""

		self._validate_port(port)

		# calculate arg to io board command
		pin_int = 0
		for pin in input_pins:
			self._validate_pin(pin)
			pin_int += 2 ** (pin - 1)

		self._set_pin_direction_raw(port,pin_int)

	def _port_pull_up_raw(self,port,arg):
		"""
		(untested) Configures pins of a port to be in "Port Pull Up" mode. From the docs:

		The Pull Up configuration applies to those lines [pins] that are set as inputs,
		writing a 0 to the corresponding bit applies a pull up resistor to the line
		so that if it is not driven low it will be pulled to a known high state, this
		is very useful if sensing contact closures or open collector outputs.
		"""
	
		self._validate_port(port)

		cmd = '#'
		self.driver.write(cmd)
		self.write_port(port, arg)

	def port_pull_up(self, port, pins=[]):
		"""
		(untested) Convenience function for the port pull up feature. See docstring for _port_pull_up_raw.
		"""

		pin_int = 255
		for pin in pins:
			self._validate_pin(pin)
			pin_int -= 2 ** (pin - 1)

		self._port_pull_up_raw(port, pin_int)

	def _set_threshold_raw(self,port,arg):
		"""
		(untested) Configures pins of a port to set the threshold at which a line reads as high or low.

		From the docs: The threshold function sets the threshold at which a line reads as
		high or low. When the corresponding bit is set as 1 then the threshold is set at
		1.4V and any voltage above this reads as a high level. When the corresponding
		threshold bit is set to 0 the threshold is set at 2.5V and any voltage above this
		reads as a high level.
		"""

		self._validate_port(port)
		cmd = '@'
		self.driver.write(cmd)
		self.write_port(port, arg)

	def set_threshold_high(self, port, pins=[]):
		"""
		(untested) Convenience function for the threshold feature. See docstring for _set_threshold_raw.
		"""

		pin_int = 255
		for pin in pins:
			self._validate_pin(pin)
			pin_int -= 2 ** (pin - 1)

		self._set_threshold_raw(port, pin_int)

	def _schmitt_trigger_raw(self,port,arg):
		"""
		(untested) Configures pins of a port to enable the Schmitt trigger. From the docs:

		Schmitt trigger inputs means that the input line is compared to 2 voltages,
		0.75V and 4.25V. When the line's voltage drops below 0.75V it will read as a
		low until the line's voltage rises above 4.25V at which time the line will
		read as a high. When the line's voltage is in between 0.75V and 4.25V, the
		value will remain at its previous level. To enable the Schmitt trigger on
		any input a 0 must be written to the corresponding bit.
		"""
	
		self._validate_port(port)

		cmd = '$'
		self.driver.write(cmd)
		self.write_port(port, arg)

	def schmitt_trigger(self, port, pins=[]):
		"""
		(untested) Convenience function for the Schmitt trigger feature.
		See docstring for _schmitt_trigger_raw.
		"""

		pin_int = 255
		for pin in pins:
			self._validate_pin(pin)
			pin_int -= 2 ** (pin - 1)

		self._schmitt_trigger_raw(port, pin_int)


if __name__ == '__main__':
	io = IOModule()
	print io.identity()

