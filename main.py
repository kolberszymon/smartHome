import machine
from time import sleep
# Micropython

try:
	switch = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP) # D1/GPIO5
except:
	print("s:e")
	switch = 0 # open

prevValue = 0

while True:
	sleep(1)
	print("s.v.: " + str( switch.value() ) )
	if prevValue != switch.value():
		if switch.value() == 1: # door opened
			print('Door Opened')
		if switch.value() == 0: # door closed
			print('Door Closed')
		try:
			prevValue = switch.value()
		except:
			prevValue = -1