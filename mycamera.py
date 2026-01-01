# 1. Any time you open a new terminal for this project, run:
# source .venv/bin/activate


#!/usr/bin/env python3
import time, os
import json
from datetime import datetime

from sense_hat import SenseHat
from picamera2 import Picamera2

from upload_cloudinary import upload_image
import paho.mqtt.client as mqtt

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "/mspi/event/pics"  # change to your own ID 

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

## --------------- Variables Global ---------------------------------------------------------------------
#use os to set up base and static folder 
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #get current directory
STATIC_DIR = os.path.join(BASE_DIR, "static") #set static directory path
os.makedirs(STATIC_DIR, exist_ok=True) #create static directory if it doesn't exist
IMAGE_PATH = os.path.join(STATIC_DIR, "last_visitor.jpg") #set image path
STATE_DIR = os.path.join(BASE_DIR, "state") #It creates a variable named STATE_DIR that points to a folder called state inside your project folder.
STATE_PATH = os.path.join(STATE_DIR, "pics.json") #It creates a variable called STATE_PATH that combines the folder location (STATE_DIR) with the specific filename pics.json.

os.makedirs(STATE_DIR, exist_ok=True) #to create the folder state if doesn't exists.


## --------------- Funtions ---------------------------------------------------------------------
# function to get temperature and humidity inforamation
def get_sensor_data():
    temp = sense.get_temperature()
    humidity = sense.get_humidity()
    return {"temperature": round(temp, 2), "humidity": round(humidity, 2)}

# function to capture the photo and grab timestamp
def capture_photo():
    print("Capturing visitor photo...")
    picam2.capture_file(IMAGE_PATH)
    sense.clear(0, 255, 0)  # flash green
    time.sleep(0.3)
    sense.clear(0, 0, 0)
    print("Photo saved to:", IMAGE_PATH) # save the jpg image

## -------------- Main --------------------------------------------------------------------------
sense = SenseHat()
sense.clear(0, 0, 0)

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()
time.sleep(2)  # Give the sensor 2 seconds to stabilize
print("Camera started. Press the Sense HAT joystick (middle) to take a photo.")

# Call capture_photo when SenseHat btn is pressed.
try:
    while True:
        for event in sense.stick.get_events():
            if event.action == "pressed" and event.direction == "middle":
                print("Button pressed at", datetime.now())
                capture_photo()
                sensor_results = get_sensor_data()

                ### Uploading to Cloudinary
                print("Uploading to cloud...")
                cloud_url = upload_image(IMAGE_PATH)
                print(f"State updated with new URL: {cloud_url}")

                # creating the object
                payload = {
                    "ts": int(time.time()),
                    "url": cloud_url,
                    "temp": sensor_results["temperature"],
                    "humidity": sensor_results["humidity"]
                }
                # writing pics.json with object information
                with open(STATE_PATH, "w") as f:
                    json.dump(payload, f)

                # send the information fro payload (stringfied) to MQTT_TOPIC
                client.publish(MQTT_TOPIC, json.dumps(payload))
                print("MQTT event published:", payload)
                
                

        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    picam2.stop() # stop camera
    sense.clear() # cleans sensehat leds (back to leds off)
    client.loop_stop() # stop MQTT loop
    client.disconnect() # Disconect MQTT
