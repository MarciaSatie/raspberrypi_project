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
        with open(STATE_PATH) as f:
            data = json.load(f)
        ts = data.get("ts") # get timestamp from json file.
        if not ts:
            return None

        url_from_file = data.get("url", "") # get image url (Cloudinary) from json file.
        data["url"] = f"{url_from_file}?ts={data['ts']}" # trick brouser's cache
        age = int(time.time()) - ts
        time_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        data["age"] = age
        data["time_str"] = time_str
        return data

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
