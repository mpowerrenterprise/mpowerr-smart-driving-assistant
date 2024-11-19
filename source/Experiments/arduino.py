from pyfirmata import Arduino
import time

# Connect to the Arduino board on COM6 (replace with your port if needed)
board = Arduino('COM6')

# Set up pin 13 as an output pin
pin_13 = board.get_pin('d:13:o')

# Blink the LED 10 times
for i in range(10):
    pin_13.write(1)  # Turn the LED on
    time.sleep(1)    # Wait for 1 second
    pin_13.write(0)  # Turn the LED off
    time.sleep(1)    # Wait for 1 second

# Close the connection to the board
board.exit()
