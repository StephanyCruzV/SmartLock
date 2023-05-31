import RPi.GPIO as GPIO
from time import sleep
from multiprocessing  import Process, Value
from ctypes import c_bool

# Define variables
Relay = 13
Push = 12
Green = 14
Red = 15
pinPassword = ""
entrada = ""

#Define flags
flagPinPad = False
flagVision = False
flagUnlock = Value(c_bool, False)

TECLA_ABAJO= True
TECLA_ARRIBA = False

# Define GPIO configuration
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(Relay, GPIO.OUT)
GPIO.setup(Green, GPIO.OUT)
GPIO.setup(Red, GPIO.OUT)
GPIO.setup(Push, GPIO.IN)

# Define variables
teclas=[['A', '3', '2', '1'], ['B', '6', '5', '4'], ['C', '9', '8', '7'], ['D', '#', '0', '*']]

#Pines del GPIO
filas=[2,3,4,5]
columnas=[6,7,8,9]

#Read Password file
def readPasswordFile():
	global pinPassword
	with open('password.txt', 'r') as file:
		data = file.readline()
		l = [int(i) for i in data if i.isdigit()]
		pinPassword = ''.join(str(j) for j in l)
	print(pinPassword)	
	file.close()
	
def savePassword(newpassword):
	with open('password.txt', 'w') as file:
		file.write(newpassword)
	print(newpassword)	
	file.close()

#define los pines de filas como salidas 
for pin in filas:
	GPIO.setup(pin, GPIO.OUT)
	
#define los pines de columnas como entradas
for pin in columnas:
	GPIO.setup(pin, GPIO.IN, pull_up_down= GPIO.PUD_DOWN)
	
def initPinPad():
	for fila in range(0,4):
		for columna in range(0,4):
			GPIO.output(filas[fila],False)
			
def scan(fila, columna):
	#Define columna actual como HIGH
	GPIO.output(filas[fila],True)
	tecla = None
	
	#verifica por teclas si hay una presionada
	if GPIO.input(columnas[columna]) == TECLA_ABAJO:
		tecla= TECLA_ABAJO
	if GPIO.input(columnas[columna]) == TECLA_ARRIBA:
		tecla= TECLA_ARRIBA
		
	GPIO.output(filas[fila],False)
	return tecla


def unlock():
	GPIO.output(Relay,True)
	
def lock():
	if not flagUnlock.value:
		GPIO.output(Relay, False)

# Todas las columnas en low
initPinPad()

def readPad():
	for fila in range (4):
		for columna in range (4):
			tecla = scan(fila, columna)
			if tecla == TECLA_ABAJO:
				sleep(0.3)
				last_key = teclas[fila][columna]
				print(last_key)
				return last_key
	return ""

def pinUnlock(userIn):
	global flagPinPad
	global entrada
	
	if len(userIn) == 6:
		if entrada == pinPassword:
			flagUnlock.value = True
			unlock()
			GPIO.output(Green,True)
			flagPinPad = True
			sleep(10)
			GPIO.output(Green,False)
			flagUnlock.value = False
			lock()
			entrada=""
		else:
			lock()
			GPIO.output(Red,True)
			sleep(1)
			GPIO.output(Red,False)
			entrada=""
			print("error")
			
def validatePassword(password, userIn):
	if userIn == password:
		return True
	else:
		return False

def changePassword():
	global pinPassword
	global flagPinPad
	gpFlag = False
	userIn = ""
	
	print("Enter Current Password")
	while not gpFlag:
		key = readPad()
		if key == '*':
			flagPinPad = True
		else:
			userIn = userIn + key
			print(userIn)
			if len(userIn) == 6:
				gpFlag = validatePassword(pinPassword, userIn)
				print(gpFlag)
				if not gpFlag:
					return

	print("Enter New Password")
	gpFlag = False
	userIn = ""
	while not gpFlag:
		key = readPad()
		if key == '*':
			flagPinPad = True
		else:
			userIn = userIn + key
			print(userIn)
			if len(userIn) == 6:
				newPassword = userIn
				gpFlag = True
				
	print("Reenter New Password to Confirm")
	
	gpFlag = False
	userIn = ""
	while not gpFlag:
		key = readPad()
		if key == '*':
			flagPinPad = True
		else:
			userIn = userIn + key
			print(userIn)
			if len(userIn) == 6:
				gpFlag = validatePassword(newPassword, userIn)
				print(gpFlag)
				if not gpFlag:
					print("Missmatch password")
					return
				else:
					print("Password changed")
					pinPassword = newPassword
					savePassword(pinPassword)
					return
	
	flagPinPad = True

def modePinPad():
	global flagPinPad
	#readPasswordFile()
	while not flagPinPad:
		global entrada
		key = readPad()
		if key == '*':
			flagPinPad = True
		elif key == '#':
			changePassword()
		else:
			entrada = entrada + key
			print(entrada)
			pinUnlock(entrada)
	flagPinPad = False
	print(" Ready, select mode")
	
	
def unlockMode():
	while True:
		mode=readPad()
		if mode == 'A':
			# Vision
			modeEric()
		if mode == 'B':
			# Unlock with PinPad
			modePinPad()

# Define Inter Button Unlock Interruption
def internUnlock(): 
	
	while True:
		if GPIO.input(Push):
			flagUnlock.value= True
			unlock()
			sleep(5)
			flagUnlock.value = False
			lock()
		else:
			lock()

def modeEric():
	global flagVision
	print(" Modo Eric Uwu")
	while not flagVision:
		key = readPad()
		if key == '*':
			flagVision = True
	print(" Ready, select mode")
	flagVision = False

if __name__ == '__main__':
	print(" Ready, select mode")
	
	readPasswordFile()

	#Define Processes
	p1 = Process(target=unlockMode)
	p2 = Process(target=internUnlock)
	
	#Start Processes
	p1.start()
	p2.start()
	
	# Wait for processes to finish
	p1.join()
	p2.join()
	
