# Any time you open a new terminal for this project, run:
# source .venv/bin/activate

import time, os
import json
from datetime import datetime

from sense_hat import SenseHat
from picamera2 import Picamera2

from upload_cloudinary import upload_image
import paho.mqtt.client as mqtt

import BlynkLib, os

import threading # to manage multitask tasks (streaming and take pictures for example)
from stream_server import run_server, get_ip # Importing methods from stream_server.py



## --------------- Variables Global ---------------------------------------------------------------------
# Blynk
BLYNK_AUTH = 'rlae8SVJlydLMI-Y41NYARtBRA2Exvpy'
# To avoid the error BlynkProtocol.__init__(self, auth, **kwargs)
# reference to fix it: https://community.blynk.cc/t/python-library-with-local-server/36835
# Initialize Blynk
# blynk = BlynkLib.Blynk(BLYNK_AUTH,
#                        server='xxx.xxx.xxx.xxx', # set server address, usually blynk.cloud
#                        port=8080,              # set server port, Port 80 is the standard "front door" for the new Blynk cloud 
#                        heartbeat=30,           # set heartbeat to 30 secs
#                        )
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# MQTT Mosquito
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "/mspi/event/pics"  
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

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
def capture_photo(sensor_results):
    print("Capturing visitor photo...")
    picam2.capture_file(IMAGE_PATH)
    print("Photo saved to:", IMAGE_PATH) # save the jpg image

    # Visual feedback on Pi - Led Green
    sense.clear(0, 255, 0)  # flash green
    time.sleep(0.3)
    sense.clear(0, 0, 0)

    # Update the Blynk Console (V0)
    current_temp = sensor_results["temperature"]
    current_humi = sensor_results["humidity"]
    blynk.virtual_write(0, current_temp) 
    blynk.virtual_write(1, current_humi) 
    print(f"Sent to Blynk: Temp {current_temp}; Humidity {current_humi} to V0, V1")

    # Trigger the Notification from Blynk
    blynk.log_event("new_pic", f"New Picture! Temp: {current_temp}C \n https://raspberrypi-project.onrender.com/")
    print("Notification triggered in Cloud -Blynk.")



# Function os Sequence of actions, take picture, upload to cloudinary, json, MQTT
def trigger_capture_sequence():    
    print("Executing Capture Sequence...")
    sensor_results = get_sensor_data()
    
    # 1. Take Photo
    capture_photo(sensor_results)
    
    # 2. Upload to Cloudinary
    print("Uploading to cloud...")
    cloud_url = upload_image(IMAGE_PATH)
    
    # 3. Create Payload
    payload = {
        "ts": int(time.time()),
        "url": cloud_url,
        "temp": sensor_results["temperature"],
        "humidity": sensor_results["humidity"]
    }
    
    # 4. Save JSON and MQTT
    with open(STATE_PATH, "w") as f:
        json.dump(payload, f)
        
    client.publish(MQTT_TOPIC, json.dumps(payload))
    print("Sequence Complete.")

    # 5 Blynk IMAGE GALLERY UPDATE
    # Change the image at all urls to a new URL
    blynk.set_property(3, "urls",cloud_url)
    print(f"Blynk Gallery Updated: {cloud_url}")


# Mobile Button to take a Picture
@blynk.on("V2")
def handle_v2_write(value):
    button_value = int(value[0])
    print(f'Current button value: {button_value}')

    if button_value ==1:
        print("Blynk App Triggered: Taking photo...")
        trigger_capture_sequence()      
   




## -------------- Main --------------------------------------------------------------------------
sense = SenseHat()
sense.clear(0, 0, 0)

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(2)  # Give the sensor 2 seconds to stabilize
print("Camera started. Press the Sense HAT joystick (middle) to take a photo.")

# 3. START STREAM SERVER IN BACKGROUND
# We pass the 'picam2' object to the server so it can use it
server_thread = threading.Thread(target=run_server, args=(picam2,))
server_thread.daemon = True
server_thread.start()

video_path = get_ip() 
print("Server is live at: {video_path}")
blynk.set_property(4, "url", video_path) # updating streaming url path at Blynk

# Call capture_photo when SenseHat btn is pressed.
try:
    while True:
        blynk.run()
        current_time = time.time()

        for event in sense.stick.get_events():
            if event.action == "pressed" and event.direction == "middle":
                trigger_capture_sequence()      

        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    picam2.stop() # stop camera
    sense.clear() # cleans sensehat leds (back to leds off)
    client.loop_stop() # stop MQTT loop
    client.disconnect() # Disconect MQTT
