#!/usr/bin/env python3
import time, os
import json
from datetime import datetime

from sense_hat import SenseHat
from picamera2 import Picamera2

#use os to set up base and static folder 
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #get current directory
STATIC_DIR = os.path.join(BASE_DIR, "static") #set static directory path
os.makedirs(STATIC_DIR, exist_ok=True) #create static directory if it doesn't exist
IMAGE_PATH = os.path.join(STATIC_DIR, "last_visitor.jpg") #set image path
STATE_DIR = os.path.join(BASE_DIR, "state") #It creates a variable named STATE_DIR that points to a folder called state inside your project folder.
STATE_PATH = os.path.join(STATE_DIR, "pics.json") #It creates a variable called STATE_PATH that combines the folder location (STATE_DIR) with the specific filename pics.json.

os.makedirs(STATE_DIR, exist_ok=True) #to create the folder state if doesn't exists.

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

    new_state = {"ts": int(time.time())} #It creates a Python dictionary (a piece of data) that stores the current time as a "timestamp"
    with open(STATE_PATH, "w") as f:
        json.dump(new_state, f) #It takes your new_state data (the timestamp) and writes it into the open file f in a format that looks like {"ts": 1735493125}.


try:
    while True:
        for event in sense.stick.get_events():
            if event.action == "pressed" and event.direction == "middle":
                print("Button pressed at", datetime.now())
                capture_photo()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    picam2.stop()
    sense.clear()
