from mqtt import MQTTClient
import machine
from time import sleep
# Micropython

client_id='ESP8266'
mqtt_server = '192.168.0.115'
topic = b'test/a'

def sub_cb(topic, msg): 
   print(msg) 

client = MQTTClient(client_id, mqtt_server) 
client.connect()

try:
	switch = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP) # D1/GPIO5
except:
	print("s:e")
	switch = 0 # open

prevValue = 0

while True:
	sleep(1)
	print("s.v.: " + str( switch.value() ) )
	client.publish(topic, msg=str(switch.value()))
	if prevValue != switch.value():
		if switch.value() == 1: # door opened
			client.publish(topic, msg='State: 1, Door Opened')
			print('Door Opened')
		if switch.value() == 0: # door closed
			client.publish(topic, msg='State: 0, Door Closed')
			print('Door Closed')
		try:
			prevValue = switch.value()
		except:
			prevValue = -1
