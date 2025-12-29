#!/usr/bin/env python3
import time, os
from datetime import datetime

from sense_hat import SenseHat
from picamera2 import Picamera2

#use os to set up base and static folder 
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #get current directory
STATIC_DIR = os.path.join(BASE_DIR, "static") #set static directory path
os.makedirs(STATIC_DIR, exist_ok=True) #create static directory if it doesn't exist
IMAGE_PATH = os.path.join(STATIC_DIR, "last_visitor.jpg") #set image path

sense = SenseHat()
sense.clear(0, 0, 0)

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()
print("Camera started. Press the Sense HAT joystick (middle) to take a photo.")

def capture_photo():
    print("Capturing visitor photo...")
    picam2.capture_file(IMAGE_PATH)
    sense.clear(0, 255, 0)  # flash green
    time.sleep(0.3)
    sense.clear(0, 0, 0)
    print("Photo saved to:", IMAGE_PATH)

try:
    while True:
        for event in sense.stick.get_events():
            if event.action == "pressed" and event.direction == "middle":
                print("Doorbell pressed at", datetime.now())
                capture_photo()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    picam2.stop()
    sense.clear()
