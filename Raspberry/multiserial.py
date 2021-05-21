import serial 
from time import sleep
from datetime import datetime
import json
import RPi.GPIO as GPIO

"""If any error or unintended output occurs, read the log file logs.txt"""

# Activate GPIO ports to select channel in multiplexer
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
#GPIO.output(23, GPIO.HIGH)
#GPIO.output(24, GPIO.HIGH)
# Define port for serial communiation
serialport = serial.Serial("/dev/serial0", baudrate=9600, timeout=10.0)

def writeToFile (filepath, msg, mode='w'):
	"""Writes or appends a string to a specified file."""
	with open(filepath, mode) as f:
		f.write(msg)
		
def runDetection ():
	"""Runs the detection process."""
	# Writes a message to the maixpy device to activate detection.
	serialport.write('send')
	# Read from the serial port and decodes to readable text.
	rcv = serialport.readline().decode('utf-8').rstrip()
	print(rcv)
	if (rcv != ""):
		# Creates object with timestamp
		rcv_obj = {'result': rcv, 'timestamp': str(datetime.now())[:-7]}
		sv_obj = json.dumps(rcv_obj)
		# Writes to files
		writeToFile('exchange_history.txt', sv_obj+'\n', 'a')
		try:
			writeToFile('exchange.txt', sv_obj+'\n')
		except:
			print("Cannot open file! Another attempt will be made in 2 seconds.")
			sleep(2)
			try:
				writeToFile('exchange.txt', sv_obj+'\n')
			except:
				print("Cannot open file! No more attempts.")
	else:
		print("Connection Timeout")
	# Turns switch off
	writeToFile('switch.txt', "0")

while True:
	# Reads the switch file
	with open('switch.txt', 'r') as f:
		try:
			on = int(f.read()) 
		except ValueError:
			print("switch.txt can only contain a number, 0 or 1.")
		else:
			# Run Detection if switch is on.
			if on:	
				runDetection()
	sleep(1)

				
							
