import time
import lcd_module


#
#   This file is supposed to be equal to main_module
#	Add this functions to that file 
#

# Check reference: 
#https://letsmakeprojects.com/interface-lcd-with-raspberry-pi-very-easily-using-i2c-and-python/
mylcd = lcd_module.lcd()
second = 0
mystr = ""
messageOption = 0

def initLCD():
	global mylcd
	global second
	global messageOption
	messageOption = 1
	displayMessage(messageOption)
	time.sleep(1)
	
	messageOption = 2
	displayMessage(messageOption)
	time.sleep(1)
	
	messageOption = 3
	displayMessage(messageOption)
	time.sleep(1)
	
	messageOption = 4
	displayMessage(messageOption)
	time.sleep(1)
	
		
def initializeLCD():
	global mylcd
	mylcd.lcd_clear()
	mylcd.lcd_display_string("READY", 1, 5)
	mylcd.lcd_display_string("SELECT MODE", 2, 2)
	
def writePassword():
	global mylcd
	global mystr
	global second
	mystr = ""
	second = 0
	while second<6:
		mystr = mystr + "*"
		mylcd.lcd_display_string(mystr, 2, 0)
		second = second + 1
		time.sleep(1)
	
def displayMessage(option):
	global mylcd
	global mystr
	if option == 1:
		initializeLCD()
	if option == 2:
		mylcd.lcd_clear()
		mylcd.lcd_display_string("ENTER ACTUAL", 1, 1)
		writePassword()
	if option == 3:
		mylcd.lcd_clear()
		mylcd.lcd_display_string("ENTER NEW", 1, 1)
		writePassword()
	if option == 4:
		mylcd.lcd_clear()
		mylcd.lcd_display_string("RE-ENTER NEW", 1, 1)
		writePassword()
		
	time.sleep(1)
	
	
