
import RPi.GPIO as GPIO
from time import sleep
from multiprocessing  import Process, Value
from ctypes import c_bool
import lcd_module

# ---------------- Define variables ----------------
Relay = 13								# Relay pin, energize with 12V
Push = 12								# Push Botton, Inside desativator
Green = 14								# Led indicator "UNLOCKED / OPEN"
Red = 15								# Led indicator "LOCK / WRONG PASSWORD"
pinPassword = ""						# Decalre variable for pinpad password
entrada = ""							# Declare variable to read pinpad input

# ---------------- Define LCD variables ----------------
mylcd = lcd_module.lcd()
second = 0
mystr = ""
messageOption = 0

# ---------------- Define Flags ----------------
flagPinPad = False						# Flag for "in PinPad Mode"
flagVision = False						# Flag "in Vision Mode"	
flagUnlock = Value(c_bool, False)		# Flag to validate intern unlock this allows
										# to Unlock and interrupt any mode safely 
TECLA_ABAJO= True						# PinPad flag for key pushed.
TECLA_ARRIBA = False					# PinPad flag for key in false.

# ---------------- GPIO Configuration ----------------
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(Relay, GPIO.OUT)
GPIO.setup(Green, GPIO.OUT)
GPIO.setup(Red, GPIO.OUT)
GPIO.setup(Push, GPIO.IN)

# ---------------- Define PinPad Matrix ----------------
teclas=[['A', '3', '2', '1'], 
		['B', '6', '5', '4'], 
		['C', '9', '8', '7'], 
		['D', '#', '0', '*']]

# ---------------- Define PinPad GPIO Pins ----------------
filas=[17,27,4,5]
columnas=[6,7,8,9]

# ---------------- Define Rows Pins as Outputs ---------------- 
for pin in filas:
	GPIO.setup(pin, GPIO.OUT)
	
# ---------------- Define Columns Pins as Inputs ----------------
for pin in columnas:
	GPIO.setup(pin, GPIO.IN, pull_up_down= GPIO.PUD_DOWN)

# ---------------- Read Password file ----------------
''' Add function description'''
def readPasswordFile():
	global pinPassword
	with open('password.txt', 'r') as file:
		data = file.readline()
		# Read digits of stored password in file
		l = [int(i) for i in data if i.isdigit()]
		# Convert list of digits into string to manipulate
		pinPassword = ''.join(str(j) for j in l)
	# Print actual password in file
	print(pinPassword)	
	file.close()

# ---------------- Save New Password in File ----------------
''' Add function description'''	
def savePassword(newpassword):
	with open('password.txt', 'w') as file:
		file.write(newpassword)
	print(newpassword)	
	file.close()


# ----------------
def displayMessage(option):
	global mylcd
	global mystr
	mylcd.lcd_clear()
	if option == 1:
		mylcd.lcd_display_string("READY", 1, 5)
		mylcd.lcd_display_string("SELECT MODE", 2, 2)
	if option == 2:
		mylcd.lcd_display_string("ENTER ACTUAL", 1, 1)
		mylcd.lcd_display_string("PASSWORD:", 2, 1)
	if option == 3:
		mylcd.lcd_display_string("ENTER NEW", 1, 1)
		mylcd.lcd_display_string("PASSWORD:", 2, 1)
	if option == 4:
		mylcd.lcd_display_string("RE-ENTER NEW", 1, 1)
		mylcd.lcd_display_string("PASSWORD:", 2, 1)
	if option == 5:
		mylcd.lcd_display_string("PINPAD UNLOCK", 1, 1)
		mylcd.lcd_display_string("PASSWORD:", 2, 1)
	if option == 6:
		mylcd.lcd_display_string("ERROR", 1, 5)
		mylcd.lcd_display_string("MISSMATCH INPUT", 2, 1)
	if option == 7:
		mylcd.lcd_display_string("SUCCESS", 1, 4)
		mylcd.lcd_display_string("PASSWORD SAVED", 2, 1)
	if option == 8:
		mylcd.lcd_display_string("SUCCESS", 1, 4)
		mylcd.lcd_display_string("DOOR UNLOKED", 2, 2)
	if option == 9:
		mylcd.lcd_display_string("ERROR", 1, 6)
		mylcd.lcd_display_string("WRONG PASSWORD", 2, 1)
	
	sleep(1)
	

# ---------------- 
def displayPass(usrinLen):
	global mylcd
	global mystr
	mystr = ""
	
	for i in usrinLen:
		mystr = mystr + "*"
	mylcd.lcd_display_string(mystr, 2, 10)
	
# ---------------- Initialize PinPad Configurations ----------------
def initPinPad():
	for fila in range(0,4):
		for columna in range(0,4):
			GPIO.output(filas[fila],False)

# ---------------- Scan PinPid Inputs ----------------
def scan(fila, columna):
	#Define actual column as HIGH
	GPIO.output(filas[fila],True)
	tecla = None
	
	# Verify if any key has been push/activated
	if GPIO.input(columnas[columna]) == TECLA_ABAJO:
		tecla= TECLA_ABAJO
	if GPIO.input(columnas[columna]) == TECLA_ARRIBA:
		tecla= TECLA_ARRIBA
		
	GPIO.output(filas[fila],False)
	# Returns key when pushed
	return tecla

# ---------------- Unlock Function ----------------
def unlock():
	GPIO.output(Relay,True)

# ---------------- Lock Function ----------------
def lock():

	if not flagUnlock.value:		
		# This avoids to lock when is not desired
		GPIO.output(Relay, False)

# ---------------- Funtion to read all PinPad ----------------
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

# ---------------- Unlock unis PinPad Password ----------------
def pinUnlock(userIn):
	global flagPinPad
	global entrada
	
	if len(userIn) == 6:
		if entrada == pinPassword:
			flagUnlock.value = True
			unlock()
			GPIO.output(Green,True)
			flagPinPad = True
			displayMessage(8)
			sleep(10)
			GPIO.output(Green,False)
			flagUnlock.value = False
			lock()
			entrada=""
		else:
			lock()
			GPIO.output(Red,True)
			displayMessage(9)
			sleep(2)
			GPIO.output(Red,False)
			entrada=""
			print("error")
			displayMessage(5)
			

# ---------------- Validate Password ----------------		
def validatePassword(password, userIn):
	if userIn == password:
		return True
	else:
		return False

# ---------------- Change PinPad Password ----------------
def changePassword():
	global pinPassword
	global flagPinPad
	
	gpFlag = False
	userIn = ""
	
	print("Enter Current Password")
	displayMessage(2)
	while not gpFlag:
		key = readPad()
		if key == '*':
			flagPinPad = True
		else:
			userIn = userIn + key
			print(userIn)
			displayPass(userIn)
			if len(userIn) == 6:
				gpFlag = validatePassword(pinPassword, userIn)
				print(gpFlag)
				if not gpFlag:
					return

	print("Enter New Password")
	displayMessage(3)
	gpFlag = False
	userIn = ""
	while not gpFlag:
		key = readPad()
		if key == '*':
			flagPinPad = True
		else:
			userIn = userIn + key
			print(userIn)
			displayPass(userIn)
			if len(userIn) == 6:
				newPassword = userIn
				gpFlag = True
				
	print("Reenter New Password to Confirm")
	displayMessage(4)
	
	gpFlag = False
	userIn = ""
	while not gpFlag:
		key = readPad()
		if key == '*':
			flagPinPad = True
		else:
			userIn = userIn + key
			print(userIn)
			displayPass(userIn)
			if len(userIn) == 6:
				gpFlag = validatePassword(newPassword, userIn)
				print(gpFlag)
				if not gpFlag:
					displayMessage(6)
					print("Missmatch password")
					return
				else:
					displayMessage(7)
					print("Password changed")
					pinPassword = newPassword
					# Save New Password in txt File
					savePassword(pinPassword)
					return
	
	flagPinPad = True

# ---------------- Functionality for PinPad Mode ----------------
def modePinPad():
	global flagPinPad
	
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
			displayPass(entrada)
			pinUnlock(entrada)
	flagPinPad = False
	displayMessage(1)
	print(" Ready, select mode")
	
# ---------------- Select Operation Mode ----------------
def unlockMode():
	while True:
		mode=readPad()
		if mode == 'A':
			# Vision
			modeEric()
		if mode == 'B':
			# Unlock with PinPad
			displayMessage(5)
			modePinPad()

# ---------------- Intern Unlock Method ----------------
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

# ---------------- Define Facial Recognition Mode ----------------
def modeEric():
	global flagVision
	print(" Modo Eric Uwu")
	while not flagVision:
		key = readPad()
		if key == '*':
			flagVision = True
	print(" Ready, select mode")
	flagVision = False

# ========================= MAIN =========================
if __name__ == '__main__':
	#initLCD()
	# Init PinPad
	initPinPad()
	displayMessage(1)
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
	
