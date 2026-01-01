#!/usr/bin/env python3
import os, json, time, datetime
from flask import Flask, render_template
import paho.mqtt.client as mqtt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")
STATE_PATH = os.path.join(STATE_DIR, "pics.json")

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "/mspi/event/pics" # This MUST match mycamera.py exactly!

app = Flask(__name__, static_folder="static")

def load_state():
    try:
        # No '/v123456/' in this URL! -- This way Render will show the last updted image, without commint it to github.
        base_url = "https://res.cloudinary.com/dycw921hz/image/upload/static/last_visitor.jpg"

        with open(STATE_PATH, "r") as f:
            data = json.load(f)
        
        # We add our OWN version (the current time) at the end 
        # to force Render to show the newest one.
        clean_url = f"{base_url}?t={int(time.time())}"
        temp = data.get("temp", "N/A")
        humi = data.get("humidity", "N/A")
        return {
                    "url": clean_url,
                    "temperature": temp,
                    "humidity": humi,
                    "time_str": datetime.datetime.now().strftime("%H:%M:%S")
                }
    except FileNotFoundError:
        return None
        
    except Exception as e:
        print("Error loading state:", e)
        return None

# --- MQTT CALLBACKS ---

def on_connect(client, userdata, flags, rc):
    print("MQTT connected with result code", rc)
    client.subscribe(MQTT_TOPIC)
    print("Subscribed to:", MQTT_TOPIC)


def on_message(client, userdata, msg):
    print("MQTT message on", msg.topic)
    payload_str = msg.payload.decode("utf-8")
    data = json.loads(payload_str)  
    with open(STATE_PATH, "w") as f:
        json.dump(data, f)
    print("State updated:", data)
   
       
# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()  # run MQTT network loop in background thread


# --- WEB ROUTES ---
@app.route("/")
def index():
    last_event = load_state()
    return render_template(
        'status.html',
        last_event=last_event
    )

# --- CALL MAIN ---
if __name__ == "__main__":
    # This allows the app to work on your Pi (port 8000) 
    # AND on Render (os.environ.get("PORT"))
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=8000, debug=True)
