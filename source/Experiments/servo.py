from pyfirmata import Arduino, util
import time

board = Arduino('COM6')  # Replace with your actual COM port
servo_pin = board.get_pin('d:9:s')  # Pin 9, Servo mode

time.sleep(2)  # Allow time for the board to initialize

servo_pin.write(180)  # Move servo to 180 degrees
time.sleep(1)
servo_pin.write(0)    # Move servo to 0 degrees
