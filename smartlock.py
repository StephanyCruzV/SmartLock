
import RPi.GPIO as GPIO
from time import sleep
from multiprocessing  import Process, Value
from ctypes import c_bool
import lcd_module

from Detector import main_app
from create_classifier import train_classifer
from create_dataset import start_capture
import cv2 


# ---------------- Define FR variables ----------------
show_menu = False
names = set()

# Leer los nombres existentes desde el archivo
with open("nameslist.txt", "r") as f:
    x = f.read()
    z = x.rstrip().split(" ")
    for i in z:
        names.add(i)

# ---------------- Define variables ----------------
Relay = 13								# Relay pin, energize with 12V
Push = 12								# Push Botton, Inside desativator
Green = 14								# Led indicator "UNLOCKED / OPEN"
Red = 15								# Led indicator "LOCK / WRONG PASSWORD"
pinPassword = ""						# Decalre variable for pinpad password
entrada = ""							# Declare variable to read pinpad input

# ---------------- Define LCD variables ----------------
mylcd = lcd_module.lcd()				# Define variable to control LCD
mystr = ""								# Define string to display

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


# ---------------- Define LCD PinPad messages ----------------
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
	if option == 10:
		mylcd.lcd_display_string("FACIAL", 1, 5)
		mylcd.lcd_display_string("RECOGNITION", 2, 2)
	
	sleep(1)
	

# ---------------- Define LCD FR messages ----------------
def messageFR(option):
	global mylcd
	global mystr
	mylcd.lcd_clear()
	if option == 1:
		mylcd.lcd_display_string("FACIAL", 1, 5)
		mylcd.lcd_display_string("RECOGNITION", 2, 2)
	if option == 2:
		mylcd.lcd_display_string("--MENU--", 1, 4)
		mylcd.lcd_display_string("1.Add 2.FaceR 3.Xit", 2, 1)
	if option == 3:
		mylcd.lcd_display_string("--USERS--", 1, 3)
		mylcd.lcd_display_string("1.U1 2.U2 3.U3", 2, 1)
	if option == 4:
		mylcd.lcd_display_string("SUCCESS", 1, 4)
		mylcd.lcd_display_string("USER RECOGNIZED", 2, 0)
	if option == 5:
		mylcd.lcd_display_string("RECOGNIZING", 1, 0)
		mylcd.lcd_display_string("USER 1 ...", 2, 0)
	if option == 6:
		mylcd.lcd_display_string("RECOGNIZING", 1, 0)
		mylcd.lcd_display_string("USER 2 ...", 2, 0)
	if option == 7:
		mylcd.lcd_display_string("RECOGNIZING", 1, 0)
		mylcd.lcd_display_string("USER 3 ...", 2, 0)
	
# ---------------- Display "*" as password character ----------------
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
			# Display Unlocked message
			displayMessage(8)
			sleep(10)
			GPIO.output(Green,False)
			flagUnlock.value = False
			lock()
			entrada=""
		else:
			lock()
			GPIO.output(Red,True)
			# Wrong Password Message
			displayMessage(9)
			sleep(2)
			GPIO.output(Red,False)
			entrada=""
			print("error")
			# Ask for password again
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
			# Display "*" for every user input
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
			# Display "*" for every user input
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
			# Display "*" for every user input
			displayPass(userIn)
			if len(userIn) == 6:
				gpFlag = validatePassword(newPassword, userIn)
				print(gpFlag)
				if not gpFlag:
					print("Missmatch password")
					displayMessage(6)
					return
				else:
					print("Password changed")
					displayMessage(7)
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
			# Display "*" for every user input
			displayPass(entrada)
			pinUnlock(entrada)
	flagPinPad = False
	displayMessage(1)
	print(" Ready, select mode")
	
# ========================= FR Functions =========================

def check_user():
	
	print("Select User: 1, 2, 3")
	messageFR(3)
	openLockFlag = False
	while not openLockFlag:
		key = readPad()
		
		if key == '1':
			messageFR(5)
			openLockFlag = main_app("User1")
		elif key == '2':
			messageFR(6)
			openLockFlag = main_app("User2")
		elif key == '3':
			messageFR(7)
			openLockFlag = main_app("User3")
	print("User Recognized")
	messageFR(4)
	cv2.destroyAllWindows()
	flagUnlock.value = True
	unlock()
	GPIO.output(Green,True)
	flagPinPad = True
	# Display Unlocked message
	displayMessage(8)
	sleep(10)
	GPIO.output(Green,False)
	flagUnlock.value = False
	lock()
	print(" Ready, select mode")
	displayMessage(1)
	unlockMode()
		


def add_user():
	print("\nElige 1, 2 o 3")
	messageFR(3)
	
	while True:
		key = readPad()
		
		if key == '1':
			names.add("User1")
			start_capture("User1")
			train_classifer("User1")
			print("Train successed")
			displayMenu()
		elif key == '2':
			names.add("User2")
			start_capture("User2")
			train_classifer("User2")
			print("Train successed")
			displayMenu()
		elif key == '3':
			names.add("User3")
			start_capture("User3")
			train_classifer("User3")
			print("Train successed")
			displayMenu()
		

def displayMenu():
	global flagVision
	
	print("\n--- Menu ---")
	print("1. Agregar un usuario")
	print("2. Verificar un usuario")
	print("*. Salir")
	messageFR(2)
	while True:
		key = readPad()
		
		if key == '1':
			add_user()
		elif key == '2':
			check_user()
		elif key == '*':
			print(" Ready, select mode")
			displayMessage(1)
			unlockMode()
	

# ---------------- Define Facial Recognition Mode ----------------
def modeEric():
	global flagVision
	global show_menu
	print(" Modo Eric Uwu")

	while not flagVision:
		displayMenu()
	print(" Ready, select mode")
	displayMessage(1)
	flagVision = False
	
# ---------------- Select Operation Mode ----------------
def unlockMode():
	while True:
		mode=readPad()
		if mode == 'A':
			# Vision
			messageFR(1)
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


# ========================= MAIN =========================
if __name__ == '__main__':
	
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
	
