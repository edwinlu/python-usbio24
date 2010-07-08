#!/usr/bin/env python

from usbio24.output import RelayModule

def test_relays(io,port):
	"""
	Tests not only each and every relay, but also this code. Runs everything
	through a basic functional check.
	"""

	from sys import stdout
	from time import sleep

	relay = RelayModule(io, port)

	mod_identity = io.identify()
	relay.reset()
	stdout.write("---\nTesting relays for %s\n---\n" % mod_identity)


	stdout.write("Turning on all relays on for three seconds: ")
	relay.set_state(range(1,9))
	sleep(3)
	relay.reset()
	stdout.write("done.\n")

	stdout.write("Activating relays in sequence: ")
	for times in range(3):
		for i in range(1,9):
			relay.activate(i)
			sleep(0.25)

	stdout.write("Deactivating relays in sequence: ")
	for times in range(3):
		for i in range(1,9):
			relay.deactivate(i)
			sleep(0.25)

	stdout.write("done.\n")

	stdout.write("Turning on pairs of relays: ")
	relay.set_state([1,8])
	sleep(0.25)
	relay.set_state([2,7])
	sleep(0.25)
	relay.set_state([3,6])
	sleep(0.25)
	relay.set_state([4,5])
	sleep(0.25)
	relay.reset()
	stdout.write("done.\n")


if __name__ == '__main__':
	from usbio24.io import IOModule
	from sys import argv, exit

	if len(argv) < 3:
		print ''
		print 'Usage: ./relays.py <device> <port>'
		print ''
		exit(1)

	io = IOModule(device=argv[1])
	test_relays(io, argv[2])

