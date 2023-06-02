import time
import lcd_module

# Check reference: 
#https://letsmakeprojects.com/interface-lcd-with-raspberry-pi-very-easily-using-i2c-and-python/

mylcd = lcd_module.lcd()

second = 0

mylcd.lcd_display_string("WEL-COME TO", 1, 3)
mylcd.lcd_display_string("SMARTLOCK", 2, 0)

time.sleep(3)

mylcd.lcd_clear()

mylcd.lcd_display_string(" I2C LCD Setup", 1, 0)
mylcd.lcd_display_string("  Raspberry Pi", 2, 0)

time.sleep(3)


mylcd.lcd_clear()

while True :
	mylcd.lcd_display_string("Hello World! Uwu", 1, 0)
	mylcd.lcd_display_string(str(second), 2, 0)
	second = second + 1
	time.sleep(1)

