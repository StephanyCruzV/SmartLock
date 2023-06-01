
from pinpadModule import *

# ========================= MAIN =========================
if __name__ == '__main__':
	# Init PinPad
	initPinPad()
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
	
