import board

from digitalio import DigitalInOut, Direction, Pull
from src.MagTagSensors import MagTagSensors

# Signal start of code execution
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT
led.value = True

# Main code
MagTagSensors()
