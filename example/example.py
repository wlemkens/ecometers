import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#import ecometers
from ecometers.ecometers import EcoMeterS
import time
import logging

def handle_result():
    print(ecometers.level)
    print(ecometers.temperature)

logging.basicConfig(level=logging.DEBUG)
ecometers = EcoMeterS("/dev/ttyUSB0", 190, 11, handle_result)

while(True):
    time.sleep(1)

print("Done")
