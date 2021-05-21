import serial
from time import sleep
from datetime import datetime
import json
import RPi.GPIO as GPIO

serialport = serial.Serial("/dev/serial0", baudrate=9600, timeout=5.0)

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.output(23, GPIO.LOW)
GPIO.output(24, GPIO.LOW)

while True: 
	serialport.write('skicka')
	#rcv = serialport.readline().decode('utf-8').rstrip()
	rcv = serialport.readline()
	print(rcv)
	with open('results.txt', 'a') as f:
		obj = {'result': rcv, 'timestamp': str(datetime.now())[:-7]}
		f.write(json.dumps(obj)+'\n')
	sleep(3)
	
