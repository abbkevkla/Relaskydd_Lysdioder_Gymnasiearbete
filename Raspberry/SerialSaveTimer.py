import serial
from time import sleep
from datetime import datetime
import json

serialport = serial.Serial("/dev/serial0", baudrate=9600, timeout=20.0)

print("Python script Running")

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
			writeToFile('logs.txt', "Following recieved string is incorrectly formatted or empty: '" + rcv + "'" + " [ timestamp: " + str(datetime.now())[:-7] + ", id: " + str(id) + " ]\n", 'a')
	writeToFile('switch.txt', "0")

while True:
	runDetection(1)
	sleep(30)
