import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#import ecometers
from ecometers.ecometers import EcoMeterS
import time
import logging

def handle_result(device):
    print(ecometers.level)
    print(ecometers.temperature)

usb_port = "/dev/ttyUSB0"
if len(sys.argv) > 1:
    usb_port = sys.argv[1]
print("Connecting on {:}".format(usb_port))
logging.basicConfig(level=logging.DEBUG)
ecometers = EcoMeterS(usb_port, 190, 11)
ecometers.add_on_data_received_callback(handle_result)

while(True):
    time.sleep(1)

print("Done")
