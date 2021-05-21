import serial
from time import sleep
from datetime import datetime
import json

serialport = serial.Serial("/dev/serial0", baudrate=9600, timeout=20.0)

"""If any error or unintended output occurs, read the log file logs.txt"""

def writeToFile (filepath, msg, mode='w'):
	with open(filepath, mode) as f:
		f.write(msg)
		
def runDetection (id):
	try:
		serialport.write('1')
		rcv = serialport.readline().decode('utf-8').rstrip()
	except:
		writeToFile('logs.txt', "Error in UART communication. Following error message was generated: " + str(sys.exc_info()[0]) + " [ timestamp: " + str(datetime.now())[:-7] + ", id: " + str(id) + " ]\n" , 'a')
	#print(rcv)
	else:
		if (len(rcv) > 28):
			rcv_obj = {'result': rcv, 'timestamp': str(datetime.now())[:-7], 'id': str(id)}
			sv_obj = json.dumps(rcv_obj)
			writeToFile('exchange_history.txt', sv_obj+'\n', 'a')
			try:
				writeToFile('exchange.txt', sv_obj+'\n')
			except:
				writeToFile('logs.txt', "Could not write the following object to exchange.txt:" + str(rcv_obj) + " [ timestamp: " + str(datetime.now())[:-7] + ", id: " + str(id) + " ]\n", 'a')
				sleep(2)
				try:
					writeToFile('exchange.txt', sv_obj+'\n')
				except:
					writeToFile('logs.txt', "Could not write the following object to exchange.txt: " + str(rcv_obj) + " (2nd attempt)" + " [ timestamp: " + str(datetime.now())[:-7] + ", id: " + str(id) + " ]\n", 'a')
		else:
			writeToFile('logs.txt', "Received string from camera board is incorrectly formatted. Either the detection failed or the cables are disconnected. Following string was recieved: '" + rcv + "'" + " [ timestamp: " + str(datetime.now())[:-7] + ", id: " + str(id) + " ]\n", 'a')
	writeToFile('switch.txt', "0")

while True:
	try:
		with open('switch.txt', 'r') as f:
			try:
				on = f.readline().replace("\n", "")
			except ValueError:
				writeToFile('logs.txt', "Failed reading switch.txt. File is incorrectly formatted." + " [ timestamp: " + str(datetime.now())[:-7] + ", id: " + on + " ]\n", 'a')
			else:
				if on != "0":	
					runDetection(on)
		sleep(1)
	except:
		writeToFile('logs.txt', "Failed to open switch.txt." + " [ timestamp: " + str(datetime.now())[:-7] + ", id: " + on + " ]\n", 'a')
